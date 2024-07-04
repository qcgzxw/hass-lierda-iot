import asyncio
import logging
from typing import Any

from homeassistant.components.light import LightEntity, LightEntityFeature, SUPPORT_BRIGHTNESS, SUPPORT_COLOR_TEMP, \
    SUPPORT_EFFECT, SUPPORT_COLOR
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LIERDA_DEVICES
from .lierda.devices.light import DeviceAttributes as LightAttributes
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
            _LOGGER.debug("setup light entry, id:" + str(device_id) + " key: " + entity_key)
            if config["type"] == Platform.LIGHT:
                light = LierdaLight(device, entity_key)
                entities.append(light)
    if entities:
        async_add_entities(entities)


class LierdaLight(LierdaEntity, LightEntity):

    def __init__(self, device, entry_key):
        super().__init__(device, entry_key)

    @property
    def is_on(self) -> bool:
        return self._device.get_attribute("power")

    @property
    def brightness(self) -> int:
        return self._device.get_attribute("brightness")

    @property
    def supported_features(self) -> LightEntityFeature:
        supported_features = LightEntityFeature(0)
        if self._device.get_attribute(LightAttributes.brightness) is not None:
            supported_features |= SUPPORT_BRIGHTNESS
        if self._device.get_attribute(LightAttributes.color_temperature) is not None:
            supported_features |= SUPPORT_COLOR_TEMP
        if self._device.get_attribute(LightAttributes.effect) is not None:
            supported_features |= SUPPORT_EFFECT
        if self._device.get_attribute(LightAttributes.rgb_color) is not None:
            supported_features |= SUPPORT_COLOR
        return supported_features

    async def async_turn_on(self, **kwargs):
        await self._device.turn_on()
        self._device.set_attribute("power", "ON")
        if "brightness" in kwargs:
            brightness = kwargs["brightness"]
            await self._device.set_brightness(brightness)
            self._device.set_attribute("brightness", brightness)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        await self._device.turn_off()
        self._device.set_attribute("power", "OFF")
        self.async_write_ha_state()

    def turn_on(self, **kwargs: Any) -> None:
        asyncio.run_coroutine_threadsafe(self.async_turn_on(**kwargs), self.hass.loop).result()

    def turn_off(self, **kwargs: Any) -> None:
        asyncio.run_coroutine_threadsafe(self.async_turn_off(**kwargs), self.hass.loop).result()
