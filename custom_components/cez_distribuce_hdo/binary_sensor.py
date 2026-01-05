"""Binary sensor platform for CEZ Distribution HDO integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_EAN, CONF_SIGNAL, DOMAIN
from .coordinator import CezHdoCoordinator


@dataclass(frozen=True, kw_only=True)
class CezHdoBinaryDescription(BinarySensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], bool | None]


DESCRIPTIONS: tuple[CezHdoBinaryDescription, ...] = (
    CezHdoBinaryDescription(
        key="low_tariff",
        translation_key="low_tariff",
        icon="mdi:cash-clock",
        value_fn=lambda d: d.get("low_tariff"),
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
            CezHdoBinaryEntity(coordinator=coordinator, entry=entry, description=desc)
            for desc in DESCRIPTIONS
        ]
    )


class CezHdoBinaryEntity(CoordinatorEntity[CezHdoCoordinator], BinarySensorEntity):
    entity_description: CezHdoBinaryDescription

    def __init__(
        self,
        coordinator: CezHdoCoordinator,
        entry: ConfigEntry,
        description: CezHdoBinaryDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry

        ean = entry.data[CONF_EAN]
        signal = entry.data[CONF_SIGNAL]

        # Stable unique_id for entity registry
        self._attr_unique_id = f"{ean}:{signal}:{description.key}"

        # Force exact default entity_id via suggested object_id
        self._attr_suggested_object_id = (
            f"{coordinator.base_object_prefix}_{description.key}"
        )

        # Group into a single device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=coordinator.base_object_prefix,
            manufacturer="ČEZ Distribuce",
            model="HDO",
            configuration_url="https://dip.cezdistribuce.cz/irj/portal/anonymous/casy-spinani/",
        )

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self.coordinator.data or {})
