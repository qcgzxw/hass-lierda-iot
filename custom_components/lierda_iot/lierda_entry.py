import logging

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, BAND
from .lierda_devices import LIERDA_DEVICES

_LOGGER = logging.getLogger(__name__)


class LierdaEntity(Entity):
    def __init__(self, device, entity_key: str):
        self._device = device
        self._device.register_update(self.update_state)
        self._config = LIERDA_DEVICES[self._device.type]["entities"][entity_key]
        self._entity_key = entity_key
        self._unique_id = f"{DOMAIN}.{self._device.device_id}_{entity_key}"
        self.entity_id = self._unique_id
        self._device_name = self._device.name

    @property
    def device(self):
        return self._device

    @property
    def device_info(self) -> DeviceInfo:
        return {
            "manufacturer": BAND,
            "model": f"{LIERDA_DEVICES[self._device.device_type]['name']} "
                     f"{self._device.link}"
                     f" ({self._device.mac_id})",
            "identifiers": {(DOMAIN, self._device.device_id)},
            "name": self._device_name,
            "serial_number": str(self._device.ddc_id),
            "sw_version": self._device.firmware_version,
        }

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def should_poll(self):
        return False

    @property
    def name(self):
        return f"{self._device_name} {self._config.get('name')}" if "name" in self._config \
            else self._device_name

    @property
    def available(self):
        return self._device.available

    @property
    def icon(self):
        return self._config.get("icon")

    def update_state(self):
        try:
            self.schedule_update_ha_state()
        except Exception as e:
            _LOGGER.debug(f"Entity {self.entity_id} update_state {repr(e)}")

    async def async_will_remove_from_hass(self):
        self._device.close()
        _LOGGER.debug(f"Entity {self.entity_id} removed")
