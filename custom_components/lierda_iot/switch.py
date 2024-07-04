import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LIERDA_DEVICES
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
            _LOGGER.debug("setup switch entry, id:" + str(device_id) + " key: " + entity_key)
            if config["type"] == Platform.SWITCH:
                switch = LierdaSwitch(device, entity_key)
                entities.append(switch)
    if entities:
        async_add_entities(entities)


class LierdaSwitch(LierdaEntity, SwitchEntity):

    def __init__(self, device, entry_key):
        super().__init__(device, entry_key)

    @property
    def is_on(self) -> bool:
        return self._device.is_on(self._entity_key)

    async def async_turn_on(self, **kwargs):
        await self._device.entry_set_attribute(self._entity_key, "ON")
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._device.entry_set_attribute(self._entity_key, "OFF")
        self.async_write_ha_state()
