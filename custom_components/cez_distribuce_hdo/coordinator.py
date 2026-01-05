"""Coordinator for CEZ Distribution HDO integration."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util
from homeassistant.util import slugify

from .const import (
    CONF_EAN,
    CONF_PREFIX,
    CONF_SIGNAL,
    DEFAULT_PREFIX,
    DEFAULT_REFRESH_INTERVAL_SECONDS,
    DEFAULT_UPDATE_INTERVAL_SECONDS,
    DOMAIN,
)

from cez_distribution_hdo import (
    ApiError,
    HttpRequestError,
    InvalidRequestError,
    InvalidResponseError,
    TariffService,
    sanitize_signal_for_entity,
    snapshot_to_dict,
)

_LOGGER = logging.getLogger(__name__)


def _is_naive(dt: datetime) -> bool:
    return dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None


def _object_prefix(prefix: str, signal: str) -> str:
    """Return base object_id prefix: 'hdo_<signal>' or '<prefix>_<signal>'."""
    sig = sanitize_signal_for_entity(
        signal
    )  # e.g., 'čez' -> 'cez', 'tariff-1' -> 'tariff_1'
    if prefix:
        return f"{slugify(prefix)}_{sig}"
    return f"{DEFAULT_PREFIX}_{sig}"


class CezHdoCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry

        self.ean: str = entry.data[CONF_EAN]
        self.signal: str = entry.data[CONF_SIGNAL]
        self.prefix: str = entry.options.get(CONF_PREFIX, "")

        tz_name = hass.config.time_zone or "UTC"
        tz = dt_util.get_time_zone(tz_name) or dt_util.UTC
        self._tz = tz
        tz_key = getattr(tz, "key", tz_name)

        self._service = TariffService(tz_name=tz_key)

        self._refresh_interval = timedelta(seconds=DEFAULT_REFRESH_INTERVAL_SECONDS)
        self._last_refresh_utc: datetime | None = None

        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=f"{DOMAIN}:{self.ean}:{self.signal}",
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL_SECONDS),
        )

    @property
    def base_object_prefix(self) -> str:
        return _object_prefix(self.prefix, self.signal)

    @property
    def device_identifier(self) -> str:
        return f"{self.ean}:{self.signal}"

    def _refresh_needed(self, now_utc: datetime) -> bool:
        return (
            self._last_refresh_utc is None
            or (now_utc - self._last_refresh_utc) >= self._refresh_interval
        )

    async def _maybe_refresh(self, now_utc: datetime) -> None:
        if not self._refresh_needed(now_utc):
            return

        try:
            await self._service.refresh(ean=self.ean)
            self._last_refresh_utc = now_utc
        except (
            HttpRequestError,
            ApiError,
            InvalidRequestError,
            InvalidResponseError,
        ) as err:
            raise UpdateFailed(str(err)) from err

    async def _async_update_data(self) -> dict[str, Any]:
        now_utc = dt_util.utcnow()

        # 1) Refresh rarely (schedules download/update)
        await self._maybe_refresh(now_utc)

        # 2) Snapshot often (computed values)
        try:
            # Reference time must be in service timezone
            now_local = now_utc.astimezone(self._tz)

            snap = self._service.snapshot(self.signal, now=now_local)
            # NOTE: snapshot_to_dict returns ISO UTC strings for datetimes
            data: dict[str, Any] = snapshot_to_dict(snap)
            return data
        except KeyError as err:
            raise UpdateFailed(str(err)) from err
        except Exception as err:
            raise UpdateFailed(f"snapshot failed: {err}") from err

    async def async_close(self) -> None:
        for name in ("async_close", "close"):
            meth = getattr(self._service, name, None)
            if callable(meth):
                try:
                    res = meth()
                    if hasattr(res, "__await__"):
                        await res  # type: ignore
                except Exception:
                    pass
