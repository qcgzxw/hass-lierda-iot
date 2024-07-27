"""Config flow for Lierda iot integration."""

from __future__ import annotations

import logging
import os
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError

from .const import *
from .lierda.core.lierda_api import LierdaAuth, LierdaApi

try:
    from homeassistant.helpers.json import save_json
except ImportError:
    from homeassistant.util.json import save_json
from homeassistant.util.json import load_json

_LOGGER = logging.getLogger(__name__)

STORAGE_PATH = f".storage/{DOMAIN}"

STEP_AUTH_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_REFRESH_INTERVAL, default=DEFAULT_REFRESH_INTERVAL): int,
        # vol.Required(CONF_FILTER_DEVICE, default=False): bool, # 未实现
        # vol.Required(CONF_REMEMBER_ME, default=True): bool, # 未实现
        vol.Required(CONF_LUX_DOMAIN, default=LIERDA_LUX_URL): vol.In(
            [LIERDA_LUX_URL, LIERDA_LSD_URL, LIERDA_HOTEL_URL]),
    }
)
STEP_INIT_OPTIONS_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_REFRESH_INTERVAL): int,
    }
)


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lierda auth."""

    VERSION = ENTRIES_VERSION

    def __init__(self):
        self.api = None
        self.auth = None
        self.config = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get options flow for this handler."""
        return LierdaConfigFlowHandler(config_entry)

    def _save_login_config(self, data: dict):
        os.makedirs(self.hass.config.path(STORAGE_PATH), exist_ok=True)
        record_file = self.hass.config.path(f"{STORAGE_PATH}/login.json")
        save_json(record_file, data)

    def _load_login_config(self):
        record_file = self.hass.config.path(f"{STORAGE_PATH}/login.json")
        return load_json(record_file, default={})

    '''deprecated'''

    def _save_devices_config(self, data: list[dict]):
        os.makedirs(self.hass.config.path(STORAGE_PATH), exist_ok=True)
        record_file = self.hass.config.path(f"{STORAGE_PATH}/devices.json")
        save_json(record_file, data)

    '''deprecated'''

    def _load_devices_config(self):
        record_file = self.hass.config.path(f"{STORAGE_PATH}/devices.json")
        return load_json(record_file, default={})

    async def validate_login(self, username: str, password: str, domain: str, save_account: bool) -> None:
        try:
            if username is None or password is None:
                raise InvalidAuth
            self.auth = LierdaAuth(username, password, domain)
            await self.auth.login()
            self.config[CONF_KEY_USER_AUTH_DATA] = self.auth.data
            if save_account:
                self._save_login_config({
                    CONF_KEY_USERNAME: username,
                    CONF_KEY_PASSWORD: password,
                    CONF_KEY_USER_AUTH_DATA: self.config[CONF_KEY_USER_AUTH_DATA],
                })

        except Exception as exception:
            if save_account:
                self._save_login_config({
                    CONF_KEY_USERNAME: username,
                    CONF_KEY_PASSWORD: password,
                })
            raise InvalidAuth

    def validate_interval(self, interval: int) -> None:
        if interval < 10:
            raise InvalidInterval
        self.config[CONF_KEY_REFRESH_INTERVAL] = interval

    async def load_all_devices(self):
        device_list = await self.get_user_device_list()
        if len(device_list) == 0:
            # todo 报错 账号下没有设备
            _LOGGER.error("账号下没有设备")
            pass
        self.config[CONF_KEY_DEVICES] = {}
        for device in device_list:
            self.config[CONF_KEY_DEVICES][device['id']] = device

    async def get_user_device_list(self) -> list[dict]:
        try:
            self.api = LierdaApi(**self.auth.data)
            resp = await self.api.get_device_list_by_user_id()
            device_list = resp['data']
            self._save_devices_config(device_list)
            return device_list
        except Exception as exception:
            _LOGGER.exception(exception)
            raise ApiError(str(exception))

    async def async_step_user(self, user_input: dict[str, Any] | None = None):

        errors: dict[str, str] = {}
        if user_input is not None:
            _LOGGER.debug(user_input)
            try:
                await self.validate_login(
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                    domain=user_input[CONF_LUX_DOMAIN],
                    save_account=True
                )
                self.validate_interval(user_input[CONF_REFRESH_INTERVAL])

                await self.load_all_devices()
                _LOGGER.debug(self.config)
                return await self._create_entry(user_input)

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidInterval:
                errors["base"] = "invalid_interval"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception as exception:
                _LOGGER.exception(str(exception))
                errors["base"] = str(exception)

        return self.async_show_form(
            step_id="user", data_schema=STEP_AUTH_DATA_SCHEMA, errors=errors
        )

    async def _create_entry(self, user_input):
        unique_id = f"{self.config[CONF_KEY_USER_AUTH_DATA]['userid']}@{LIERDA_API_LIST[user_input[CONF_LUX_DOMAIN]]}"
        _LOGGER.debug(unique_id)
        await self.async_set_unique_id(unique_id)

        _LOGGER.debug(self.config)

        return self.async_create_entry(
            title=unique_id,
            data=self.config,
        )


def schema_defaults(schema, dps_list=None, **defaults):
    """Create a new schema with default values filled in."""
    copy = schema.extend({})
    for field, field_type in copy.schema.items():
        if isinstance(field_type, vol.In):
            value = None
            for dps in dps_list or []:
                if dps.startswith(f"{defaults.get(field)} "):
                    value = dps
                    break

            if value in field_type.container:
                field.default = vol.default_factory(value)
                continue

        if field.schema in defaults:
            field.default = vol.default_factory(defaults[field])
    return copy


class LierdaConfigFlowHandler(OptionsFlow):
    """Handle a config flow for Lierda iot options."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        old_refresh_interval = self.hass.data[DOMAIN][CONF_KEY_REFRESH_INTERVAL] \
            if CONF_KEY_REFRESH_INTERVAL in self.hass.data[DOMAIN] \
            else DEFAULT_REFRESH_INTERVAL
        defaults = {CONF_REFRESH_INTERVAL: old_refresh_interval}

        if user_input is not None:
            refresh_interval = user_input.get(CONF_REFRESH_INTERVAL, old_refresh_interval)
            self.hass.data[DOMAIN][CONF_REFRESH_INTERVAL] = refresh_interval

            for device_id, device in self.hass.data[DOMAIN][LIERDA_DEVICES].items():
                device.set_refresh_interval(refresh_interval)

            return self.async_create_entry(title="init", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=schema_defaults(STEP_INIT_OPTIONS_DATA_SCHEMA, **defaults),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
    pass


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
    pass


class InvalidInterval(HomeAssistantError):
    """Error to indicate there is invalid auth."""
    pass


class ApiError(HomeAssistantError):
    """Error to indicate there is invalid auth."""
    pass
