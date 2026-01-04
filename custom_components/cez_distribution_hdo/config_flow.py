"""Config flow for CEZ Distribution HDO integration."""

from __future__ import annotations

import re
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.util import dt as dt_util
from homeassistant.util import slugify

from .const import DOMAIN

from cez_distribution_hdo import TariffService


CONF_EAN = "ean"
CONF_PREFIX = "prefix"
CONF_SIGNAL = "signal"

EAN_RE = re.compile(r"^\d{18}$")


def _normalize_ean(value: str) -> str:
    return value.replace(" ", "").strip()


def _validate_ean(value: str) -> str:
    value = _normalize_ean(value)
    if not EAN_RE.fullmatch(value):
        raise vol.Invalid("invalid_ean")
    return value


def _validate_prefix(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if not slugify(value):
        raise vol.Invalid("invalid_prefix")
    if len(slugify(value)) < 2:
        raise vol.Invalid("invalid_prefix")
    return value


STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EAN): vol.All(str, _validate_ean),
        vol.Optional(CONF_PREFIX, default=""): vol.All(str, _validate_prefix),
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for CEZ Distribution HDO.

    :param domain: The domain of the integration.
    """

    VERSION = 1

    def __init__(self) -> None:
        self._ean: str | None = None
        self._prefix: str = ""
        self._signals: list[str] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            ean = _normalize_ean(user_input[CONF_EAN])
            prefix = (user_input.get(CONF_PREFIX) or "").strip()

            try:
                tz_name = self.hass.config.time_zone or "UTC"
                tz = dt_util.get_time_zone(tz_name) or dt_util.UTC
                tz_key = getattr(tz, "key", tz_name)

                service = TariffService(tz_name=tz_key)
                await service.refresh(ean=ean)
                signals = list(service.signals or [])
            except (
                Exception
            ):  # keep broad; narrow later to aiohttp / library exceptions
                errors["base"] = "cannot_connect"
            else:
                if not signals:
                    errors["base"] = "no_signals"
                else:
                    self._ean = ean
                    self._prefix = prefix
                    self._signals = sorted(signals)

                    if len(self._signals) == 1:
                        return await self._create_entry(signal=self._signals[0])

                    return await self.async_step_signal()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    async def async_step_signal(self, user_input: dict[str, Any] | None = None):
        """Select HDO signal when multiple are available for the given EAN."""
        if user_input is not None:
            return await self._create_entry(signal=user_input[CONF_SIGNAL])

        options = [
            selector.SelectOptionDict(value=s, label=s) for s in (self._signals or [])
        ]

        schema = vol.Schema(
            {
                vol.Required(CONF_SIGNAL): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )

        return self.async_show_form(step_id="signal", data_schema=schema)

    async def _create_entry(self, signal: str):
        """Create config entry for EAN + selected signal.

        unique_id is composed as "{ean}:{signal}" to allow multiple signals per EAN.
        """
        assert self._ean is not None

        ean = self._ean
        prefix = self._prefix

        unique_id = f"{ean}:{signal}"
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()

        title = f"{prefix} ({signal})" if prefix else f"HDO ({signal})"

        # Store only stable identifiers in data; put user-tweakable fields into options.
        entry = self.async_create_entry(
            title=title,
            data={
                CONF_EAN: ean,
                CONF_SIGNAL: signal,
            },
            options={
                CONF_PREFIX: prefix,
            },
        )
        return entry

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow - allow changing prefix without re-adding the integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry  # type: ignore

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            prefix = (user_input.get(CONF_PREFIX) or "").strip()
            # Only store the prefix in options
            return self.async_create_entry(title="", data={CONF_PREFIX: prefix})

        current_prefix = self.config_entry.options.get(CONF_PREFIX, "")

        schema = vol.Schema(
            {
                vol.Optional(CONF_PREFIX, default=current_prefix): vol.All(
                    str, _validate_prefix
                )
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
