# custom_components/lierda_iot/light.py
"""Light platform for Lierda IoT."""

import logging
from typing import Any

from homeassistant.components.light import LightEntity, ColorMode
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
    """Set up Lierda IoT lights from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    client = hass.data[DOMAIN][config_entry.entry_id]["client"]

    entities = []

    # Create light entities for each device
    for device_id, device in coordinator.data.items():
        # Get device type configuration
        if device.type not in LIERDA_DEVICES:
            continue

        device_config = LIERDA_DEVICES[device.type]

        # Create entities based on device type configuration
        for entity_key, config in device_config["entities"].items():
            if config["type"] == Platform.LIGHT:
                entities.append(
                    LierdaLight(
                        coordinator,
                        device,
                        entity_key,
                        config,
                        client,
                    )
                )

    async_add_entities(entities)


class LierdaLight(CoordinatorEntity[LierdaDataUpdateCoordinator], LightEntity):
    """Representation of a Lierda IoT light."""

    def __init__(
        self,
        coordinator: LierdaDataUpdateCoordinator,
        device: Device,
        entity_key: str,
        config: dict[str, Any],
        client: LierdaClient,
    ) -> None:
        """Initialize the light."""
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

        # Set supported color modes
        supported_color_modes = set()
        if device.get_attribute("LEV") is not None:
            supported_color_modes.add(ColorMode.BRIGHTNESS)
        if not supported_color_modes:
            supported_color_modes.add(ColorMode.ONOFF)

        self._attr_supported_color_modes = supported_color_modes

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        if self.coordinator.data:
            device = self.coordinator.data.get(self.device.id)
            if device:
                power = device.get_attribute("SWI")
                # Power can be "ON"/"OFF" string or boolean
                if isinstance(power, str):
                    return power == "ON"
                return bool(power)
        return False

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light."""
        if self.coordinator.data:
            device = self.coordinator.data.get(self.device.id)
            if device:
                brightness = device.get_attribute("LEV")
                if brightness is not None:
                    return int(brightness)
        return None

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.device.mac_id)},
            "name": self.device.name,
            "manufacturer": "Lierda iot",
            "model": f"{LIERDA_DEVICES[self.device.type]['name']} {self.device.link} ({self.device.mac_id})",
            "sw_version": self.device.firmware_version,
            "serial_number": str(self.device.ddc_id),
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
        """Turn the light on."""
        try:
            # Turn on the light
            await self.client.set_device_attribute(
                self.device.id,
                self.device.mac_id,
                self.device.ddc_mac,
                "SWI",
                "ON",
            )

            # Optionally handle brightness
            if "brightness" in kwargs:
                brightness = kwargs["brightness"]
                await self.client.set_device_attribute(
                    self.device.id,
                    self.device.mac_id,
                    self.device.ddc_mac,
                    "LEV",
                    str(brightness),
                )

            # Optimistically update state
            self.device.attributes["SWI"] = "ON"
            if self.device.id in self.coordinator.data:
                self.coordinator.data[self.device.id].attributes["SWI"] = "ON"
            if "brightness" in kwargs:
                self.device.attributes["LEV"] = str(kwargs["brightness"])
                if self.device.id in self.coordinator.data:
                    self.coordinator.data[self.device.id].attributes["LEV"] = str(kwargs["brightness"])
            self.async_write_ha_state()
        except Exception as err:
            _LOGGER.error("Failed to turn on light %s: %s", self.device.id, err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        try:
            await self.client.set_device_attribute(
                self.device.id,
                self.device.mac_id,
                self.device.ddc_mac,
                "SWI",
                "OFF",
            )

            # Optimistically update state
            self.device.attributes["SWI"] = "OFF"
            if self.device.id in self.coordinator.data:
                self.coordinator.data[self.device.id].attributes["SWI"] = "OFF"
            if "brightness" in kwargs:
                self.device.attributes["LEV"] = str(kwargs["brightness"])
                if self.device.id in self.coordinator.data:
                    self.coordinator.data[self.device.id].attributes["LEV"] = str(kwargs["brightness"])
            self.async_write_ha_state()
        except Exception as err:
            _LOGGER.error("Failed to turn off light %s: %s", self.device.id, err)
