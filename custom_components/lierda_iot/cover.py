# custom_components/lierda_iot/cover.py
"""Cover platform for Lierda IoT."""

import logging
from typing import Any

from homeassistant.components.cover import CoverEntity, CoverEntityFeature, CoverDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import LierdaClient
from .const import DOMAIN
from .coordinator import LierdaDataUpdateCoordinator
from .lierda_devices import LIERDA_DEVICES
from .models.device import Device

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Lierda IoT covers from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][config_entry.entry_id]["client"]

    entities = []

    # Create cover entities for each device
    for device_id, device in coordinator.data.items():
        # Get device type configuration
        if device.type not in LIERDA_DEVICES:
            continue

        device_config = LIERDA_DEVICES[device.type]

        # Create entities based on device type configuration
        for entity_key, config in device_config["entities"].items():
            if config["type"] == Platform.COVER:
                entities.append(
                    LierdaCover(
                        coordinator,
                        device,
                        entity_key,
                        config,
                        client,
                    )
                )

    async_add_entities(entities)


class LierdaCover(CoordinatorEntity[LierdaDataUpdateCoordinator], CoverEntity):
    """Representation of a Lierda IoT cover."""

    def __init__(
        self,
        coordinator: LierdaDataUpdateCoordinator,
        device: Device,
        entity_key: str,
        config: dict[str, Any],
        client: LierdaClient,
    ) -> None:
        """Initialize the cover."""
        super().__init__(coordinator)
        self.device = device
        self.entity_key = entity_key
        self._config = config
        self.client = client

        # Set entity properties
        self._attr_name = f"{device.name} {config.get('name')}" if "name" in config else device.name
        self._attr_unique_id = f"{device.mac_id}_{entity_key}"

        # Set icon if provided
        if "icon" in config:
            self._attr_icon = config["icon"]

        # Set device class if provided
        if "device_class" in config:
            self._attr_device_class = config["device_class"]

        # Set supported features
        supported_features = CoverEntityFeature(0)
        if device.get_attribute("WIN") is not None:
            supported_features |= CoverEntityFeature.OPEN
            supported_features |= CoverEntityFeature.CLOSE
            supported_features |= CoverEntityFeature.STOP
        if device.get_attribute("LEV") is not None:
            supported_features |= CoverEntityFeature.SET_POSITION
        self._attr_supported_features = supported_features

    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed."""
        if self.coordinator.data:
            device = self.coordinator.data.get(self.device.id)
            if device:
                window = device.get_attribute("WIN")
                if window is None or window == "STOP":
                    return None
                if window == "CLOSE":
                    return True
                return False
        return None

    @property
    def current_cover_position(self) -> int | None:
        """Return current position of cover. 0 is closed, 100 is fully open."""
        if self.coordinator.data:
            device = self.coordinator.data.get(self.device.id)
            if device:
                level = device.get_attribute("LEV")
                if level is not None:
                    return int(level)
        return None

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.device.mac_id)},
            "name": self.device.name,
            "manufacturer": "Lierda iot",
            "model": f"{LIERDA_DEVICES[self.device.type]['name']} ({self.device.mac_id})",
            "sw_version": self.device.firmware_version,
            "serial_number": str(self.device.id),
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.device.id in self.coordinator.data
            and self.coordinator.data[self.device.id].available
        )

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        try:
            await self.client.set_device_attribute(
                self.device.id,
                self.device.mac_id,
                self.device.ddc_mac,
                "WIN",
                "OPEN",
            )
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to open cover %s: %s", self.device.id, err)

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        try:
            await self.client.set_device_attribute(
                self.device.id,
                self.device.mac_id,
                self.device.ddc_mac,
                "WIN",
                "CLOSE",
            )
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to close cover %s: %s", self.device.id, err)

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        try:
            await self.client.set_device_attribute(
                self.device.id,
                self.device.mac_id,
                self.device.ddc_mac,
                "WIN",
                "STOP",
            )
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to stop cover %s: %s", self.device.id, err)

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        try:
            position = kwargs.get("position")
            if position is None:
                return

            await self.client.set_device_attribute(
                self.device.id,
                self.device.mac_id,
                self.device.ddc_mac,
                "LEV",
                str(position),
            )
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to set cover position %s: %s", self.device.id, err)
