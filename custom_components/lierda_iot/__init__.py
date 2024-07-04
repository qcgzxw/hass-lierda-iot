from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import *
from .lierda.core.lierda_api import LierdaApi
from .lierda.devices import device_selector

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config_entry: dict):
    _LOGGER.debug(config_entry)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][CONF_RELOAD_FLAG] = {}
    hass.data[DOMAIN][CONF_KEY_REFRESH_INTERVAL] = {}
    hass.data[DOMAIN][LIERDA_DEVICES] = {}
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Lierda iot from a config entry."""
    _LOGGER.debug(config_entry.data)
    if config_entry.entry_id in hass.data[DOMAIN][CONF_RELOAD_FLAG]:
        await async_reload_entry(hass, config_entry)

    devices = {}
    hass.data[DOMAIN][CONF_KEY_USER_AUTH_DATA] = config_entry.data.get(CONF_KEY_USER_AUTH_DATA)
    hass.data[DOMAIN][CONF_KEY_REFRESH_INTERVAL] = config_entry.data.get(CONF_KEY_REFRESH_INTERVAL,
                                                                         DEFAULT_REFRESH_INTERVAL)

    async def setup_entities(device_ids: list[str]) -> None:
        for device_id in device_ids:
            device = device_selector(
                auth_data=config_entry.data[CONF_KEY_USER_AUTH_DATA],
                **config_entry.data[CONF_KEY_DEVICES][device_id]
            )
            if device is not None:
                device.set_refresh_interval(hass.data[DOMAIN][CONF_KEY_REFRESH_INTERVAL])
                device.open()
                devices[device_id] = device

    if config_entry.data.get(CONF_KEY_DEVICES):
        await setup_entities(config_entry.data[CONF_KEY_DEVICES].keys())

        if not devices:
            _LOGGER.error("No devices were set up. Check your configuration.")
            return False

        hass.data[DOMAIN][LIERDA_DEVICES] = devices

        await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def refresh_device_statuses(hass: HomeAssistant) -> None:
    """Refresh the status of all Lierda devices."""
    _LOGGER.debug("Refreshing device statuses")
    api = LierdaApi(**hass.data[DOMAIN][CONF_KEY_USER_AUTH_DATA])
    try:
        new_device_list = await api.get_device_list_by_user_id()
        _LOGGER.debug(new_device_list['data'])
        '''
        new_device_list = await api.get_device_list_by_user_id()
        devices = hass.data[DOMAIN][LIERDA_DEVICES]if len(devices) == 0 or len(new_device_list['data']) == 0:
            return
        for device_id, device in devices.items():
            for new_device in new_device_list['data']:
                if device_id == new_device['id']:
                    await device.refresh_status()
                    break
        '''
        # todo update device attribute
        # todo ha state machine
    except Exception as e:
        _LOGGER.error(f"Failed to refresh device statuses: {e}")


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    for device_id, device in hass.data[DOMAIN][LIERDA_DEVICES].items():
        device.close()
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    pass
