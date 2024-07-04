import logging

from homeassistant.components.cover import CoverEntity, CoverEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LIERDA_DEVICES
from .lierda.devices.curtain import DeviceAttributes as CurtainAttributes
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
            _LOGGER.debug("setup cover entry, id:" + str(device_id) + " key: " + entity_key)
            if config["type"] == Platform.COVER:
                cover = LierdaCurtain(device, entity_key)
                entities.append(cover)
    if entities:
        async_add_entities(entities)


class LierdaCover(LierdaEntity, CoverEntity):

    def __init__(self, device, entry_key):
        super().__init__(device, entry_key)

    @property
    def device_class(self) -> str:
        return self._config.get("device_class")

    @property
    def is_closed(self) -> bool | None:
        mode = self._device.get_attribute(CurtainAttributes.window)
        if mode is None or mode == CurtainAttributes.CURTAIN_MODE_STOP:
            return None
        if mode == CurtainAttributes.CURTAIN_MODE_CLOSE:
            return True
        return False

    @property
    def supported_features(self) -> CoverEntityFeature:
        supported_features = CoverEntityFeature(0)
        if self._device.get_attribute(CurtainAttributes.window) is not None:
            supported_features |= CoverEntityFeature.OPEN
            supported_features |= CoverEntityFeature.CLOSE
            supported_features |= CoverEntityFeature.STOP
        return supported_features

    async def async_open_cover(self, **kwargs):
        await self._device.entry_set_attribute(CurtainAttributes.window, CurtainAttributes.CURTAIN_MODE_OPEN)
        self.async_write_ha_state()

    async def async_close_cover(self, **kwargs):
        await self._device.entry_set_attribute(CurtainAttributes.window, CurtainAttributes.CURTAIN_MODE_CLOSE)
        self.async_write_ha_state()

    async def async_stop_cover(self, **kwargs):
        await self._device.entry_set_attribute(CurtainAttributes.window, CurtainAttributes.CURTAIN_MODE_STOP)
        self.async_write_ha_state()


class LierdaCurtain(LierdaCover):
    pass
