# custom_components/lierda_iot/switch.py
"""Switch platform for Lierda IoT."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up Lierda IoT switches from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][config_entry.entry_id]["client"]

    entities = []

    # Create switch entities for each device
    for device_id, device in coordinator.data.items():
        # Get device type configuration
        if device.type not in LIERDA_DEVICES:
            _LOGGER.debug("Unknown device type %s for device %s", device.type, device_id)
            continue

        device_config = LIERDA_DEVICES[device.type]

        # Create entities based on device type configuration
        for entity_key, config in device_config["entities"].items():
            if config["type"] == Platform.SWITCH:
                entities.append(
                    LierdaSwitch(
                        coordinator,
                        device,
                        entity_key,
                        config,
                        client,
                    )
                )

    async_add_entities(entities)


class LierdaSwitch(CoordinatorEntity[LierdaDataUpdateCoordinator], SwitchEntity):
    """Representation of a Lierda IoT switch."""

    def __init__(
        self,
        coordinator: LierdaDataUpdateCoordinator,
        device: Device,
        entity_key: str,
        config: dict[str, Any],
        client: LierdaClient,
    ) -> None:
        """Initialize the switch."""
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

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        if self.coordinator.data:
            device = self.coordinator.data.get(self.device.id)
            if device:
                # Get the attribute value using entity_key (e.g., "ky1" -> "KY1")
                attribute_name = self.entity_key.upper()
                value = device.get_attribute(attribute_name)
                if value:
                    return value == "ON"
        return False

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.device.mac_id)},
            "name": self.device.name,
            "manufacturer": "Lierda",
            "model": f"{LIERDA_DEVICES[self.device.type]['name']} ({self.device.mac_id})",
            "sw_version": self.device.firmware_version,
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.device.id in self.coordinator.data
            and self.coordinator.data[self.device.id].available
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        try:
            # Use uppercase entity_key (e.g., "ky1" -> "KY1")
            attribute_name = self.entity_key.upper()
            await self.client.set_device_attribute(
                self.device.id,
                self.device.mac_id,
                str(self.device.ddc_id),
                attribute_name,
                "ON",
            )
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn on switch %s: %s", self.device.id, err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        try:
            # Use uppercase entity_key (e.g., "ky1" -> "KY1")
            attribute_name = self.entity_key.upper()
            await self.client.set_device_attribute(
                self.device.id,
                self.device.mac_id,
                str(self.device.ddc_id),
                attribute_name,
                "OFF",
            )
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Failed to turn off switch %s: %s", self.device.id, err)
