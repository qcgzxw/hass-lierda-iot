# custom_components/lierda_iot/sensor.py
"""Sensor platform for Lierda IoT."""

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
    """Set up Lierda IoT sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    entities = []

    # Create sensor entities for each device
    for device_id, device in coordinator.data.items():
        # Get device type configuration
        if device.type not in LIERDA_DEVICES:
            continue

        device_config = LIERDA_DEVICES[device.type]

        # Create entities based on device type configuration
        for entity_key, config in device_config["entities"].items():
            if config["type"] == Platform.SENSOR:
                entities.append(
                    LierdaSensor(
                        coordinator,
                        device,
                        entity_key,
                        config,
                    )
                )

    async_add_entities(entities)


class LierdaSensor(CoordinatorEntity[LierdaDataUpdateCoordinator], SensorEntity):
    """Representation of a Lierda IoT sensor."""

    def __init__(
        self,
        coordinator: LierdaDataUpdateCoordinator,
        device: Device,
        entity_key: str,
        config: dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.device = device
        self.entity_key = entity_key
        self._config = config

        # Set entity properties
        self._attr_name = f"{device.name} {config.get('name')}" if "name" in config else device.name
        self._attr_unique_id = f"{device.mac_id}_{entity_key}"

        # Set sensor properties from config
        if "device_class" in config:
            self._attr_device_class = config["device_class"]
        if "unit" in config:
            self._attr_native_unit_of_measurement = config["unit"]
        if "state_class" in config:
            self._attr_state_class = config["state_class"]
        if "icon" in config:
            self._attr_icon = config["icon"]

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data:
            device = self.coordinator.data.get(self.device.id)
            if device:
                # Map entity_key to actual API attribute names
                attribute_mapping = {
                    "battery_voltage": "BAT",
                    "battery_percentage": "_BAT",
                }

                # Get the actual attribute name
                attr_name = attribute_mapping.get(self.entity_key, self.entity_key.upper())
                value = device.get_attribute(attr_name)

                if value is None:
                    return None

                # Process value based on entity type
                if self.entity_key == "battery_percentage":
                    # Remove "%" suffix if present
                    if isinstance(value, str) and value.endswith("%"):
                        return int(value.removesuffix("%"))
                    return int(value)
                elif self.entity_key == "battery_voltage":
                    return float(value)

                return value
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
