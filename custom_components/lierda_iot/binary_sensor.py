import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    LIERDA_DEVICES
)
from .lierda_devices import LIERDA_DEVICES as ALL_DEVICES
from .lierda_entry import LierdaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
):
    lierda_devices = hass.data[DOMAIN][LIERDA_DEVICES]
    entities = []
    for device_id, device in lierda_devices.items():
        for entity_key, config in ALL_DEVICES[device.device_type]["entities"].items():
            _LOGGER.debug("setup binary sensor entry, id:" + str(device_id) + " key: " + entity_key)
            if config["type"] == Platform.BINARY_SENSOR:
                sensor = LierdaBinarySensor(device, entity_key)
                entities.append(sensor)
    if len(entities) > 0:
        async_add_entities(entities)


class LierdaBinarySensor(LierdaEntity, BinarySensorEntity):

    def __init__(self, device, entry_key):
        super().__init__(device, entry_key)

    @property
    def device_class(self) -> str:
        return self._config.get("device_class")

    @property
    def is_on(self) -> bool:
        return self.device.get_attribute(self._entity_key)
