"""Common base entity for CEZ Distribution HDO integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_PREFIX, CONF_SIGNAL, DOMAIN
from .coordinator import CezHdoCoordinator
from .utils import object_prefix


class CezHdoBaseEntity(CoordinatorEntity[CezHdoCoordinator]):
    """Base CEZ Distribution HDO entity."""

    _coordinator: CezHdoCoordinator
    _attr_has_entity_name = True
    _description: str
    _entry: ConfigEntry
    _signal: str

    def __init__(
        self,
        coordinator: CezHdoCoordinator,
        entry: ConfigEntry,
        description: str,
    ) -> None:
        """Initialize the CEZ Distribution HDO base entity."""
        super().__init__(coordinator)

        self._coordinator = coordinator
        self._description = description
        self._entry = entry
        self._signal = entry.data[CONF_SIGNAL]
        prefix: str = object_prefix(
            entry.options.get(CONF_PREFIX, "") or "", self._signal
        )

        # Stable unique_id for entity registry
        self._attr_unique_id = f"{prefix}_{description}"

        # Group into a single device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
        )

    @property
    def device_info(self) -> DeviceInfo:  # noqa: D102
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._coordinator.base_object_prefix,
            "manufacturer": "ČEZ Distribuce",
            "serial_number": self._signal,
            "model": "HDO",
            "configuration_url": "https://dip.cezdistribuce.cz/irj/portal/anonymous/casy-spinani/",
        }
