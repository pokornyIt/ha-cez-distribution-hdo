"""Sensor platform for CEZ Distribution HDO integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import e
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import CONF_EAN, CONF_SIGNAL, DOMAIN
from .coordinator import CezHdoCoordinator


@dataclass(frozen=True, kw_only=True)
class CezHdoSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]
    attrs_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None


def _dt(v: Any) -> datetime | None:
    """Convert snapshot_to_dict ISO UTC string to datetime for TIMESTAMP sensors."""
    if v is None:
        return None
    if isinstance(v, datetime):
        return v
    if isinstance(v, str):
        parsed = dt_util.parse_datetime(v)
        if parsed is None:
            return None
        # Ensure tz-aware; snapshot_to_dict should already be UTC, but be defensive
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt_util.UTC)
        return parsed
    return None


DESCRIPTIONS: tuple[CezHdoSensorDescription, ...] = (
    CezHdoSensorDescription(
        key="actual_tariff",
        translation_key="actual_tariff",
        icon="mdi:swap-horizontal",
        value_fn=lambda d: d.get("actual_tariff"),
    ),
    CezHdoSensorDescription(
        key="actual_tariff_start",
        translation_key="actual_tariff_start",
        icon="mdi:clock-start",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda d: _dt(d.get("actual_tariff_start")),
    ),
    CezHdoSensorDescription(
        key="actual_tariff_end",
        translation_key="actual_tariff_end",
        icon="mdi:clock-end",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda d: _dt(d.get("actual_tariff_end")),
    ),
    CezHdoSensorDescription(
        key="next_low_tariff_start",
        translation_key="next_low_tariff_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-night",
        value_fn=lambda d: _dt(d.get("next_low_tariff_start")),
    ),
    CezHdoSensorDescription(
        key="next_low_tariff_end",
        translation_key="next_low_tariff_end",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-night",
        value_fn=lambda d: _dt(d.get("next_low_tariff_end")),
    ),
    CezHdoSensorDescription(
        key="next_high_tariff_start",
        translation_key="next_high_tariff_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-sunny",
        value_fn=lambda d: _dt(d.get("next_high_tariff_start")),
    ),
    CezHdoSensorDescription(
        key="next_high_tariff_end",
        translation_key="next_high_tariff_end",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:weather-sunny",
        value_fn=lambda d: _dt(d.get("next_high_tariff_end")),
    ),
    CezHdoSensorDescription(
        key="next_switch",
        translation_key="next_switch",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-alert",
        value_fn=lambda d: _dt(d.get("next_switch")),
    ),
    # remain_actual: recommended to expose as seconds for automation reliability
    CezHdoSensorDescription(
        key="remain_actual",
        translation_key="remain_actual",
        icon="mdi:timer-sand",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        value_fn=lambda d: d.get("remain_actual_seconds"),
        attrs_fn=lambda d: {
            "remain_actual": d.get("remain_actual"),  # HH:MM:SS string from lib
            "remain_actual_seconds": d.get("remain_actual_seconds"),
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: CezHdoCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            CezHdoSensorEntity(coordinator=coordinator, entry=entry, description=desc)
            for desc in DESCRIPTIONS
        ]
    )


class CezHdoSensorEntity(CoordinatorEntity[CezHdoCoordinator], SensorEntity):
    entity_description: CezHdoSensorDescription

    def __init__(
        self,
        coordinator: CezHdoCoordinator,
        entry: ConfigEntry,
        description: CezHdoSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry

        ean = entry.data[CONF_EAN]
        signal = entry.data[CONF_SIGNAL]

        self._attr_unique_id = f"{ean}:{signal}:{description.key}"

        # Force exact default entity_id via suggested object_id
        self._attr_suggested_object_id = (
            f"{coordinator.base_object_prefix}_{description.key}"
        )

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=coordinator.base_object_prefix,
            manufacturer="ČEZ Distribuce",
            model="HDO",
            configuration_url="https://dip.cezdistribuce.cz/irj/portal/anonymous/casy-spinani/",
        )

    @property
    def native_value(self):
        return self.entity_description.value_fn(self.coordinator.data or {})

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.attrs_fn is None:
            return None
        return self.entity_description.attrs_fn(self.coordinator.data or {})
