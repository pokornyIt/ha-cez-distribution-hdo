"""Binary sensor platform for CEZ Distribution HDO integration."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


from .const import DOMAIN
from .coordinator import CezHdoCoordinator
from .entity import CezHdoBaseEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class CezHdoBinaryDescription(BinarySensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], bool | None]


BINARY_SENSOR_DESCRIPTIONS: tuple[CezHdoBinaryDescription, ...] = (
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
    for desc in BINARY_SENSOR_DESCRIPTIONS:
        async_add_entities(
            [CezHdoBinaryEntity(coordinator=coordinator, entry=entry, description=desc)]
        )


class CezHdoBinaryEntity(CezHdoBaseEntity, BinarySensorEntity):
    entity_description: CezHdoBinaryDescription

    def __init__(
        self,
        coordinator: CezHdoCoordinator,
        entry: ConfigEntry,
        description: CezHdoBinaryDescription,
    ) -> None:
        super().__init__(coordinator, entry, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self._coordinator.data or {})
