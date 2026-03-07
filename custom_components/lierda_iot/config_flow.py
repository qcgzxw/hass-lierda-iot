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
from .api import LierdaClient
from .api.exceptions import LierdaApiError, LierdaAuthError, LierdaConnectionError, LierdaTimeoutError
from .models.auth import AuthData

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

    VERSION = ENTRY_VERSION

    def __init__(self):
        self.config = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get options flow for this handler."""
        return LierdaConfigFlowHandler()

    def _save_login_config(self, data: dict):
        os.makedirs(self.hass.config.path(STORAGE_PATH), exist_ok=True)
        record_file = self.hass.config.path(f"{STORAGE_PATH}/login.json")
        save_json(record_file, data)

    def _load_login_config(self):
        record_file = self.hass.config.path(f"{STORAGE_PATH}/login.json")
        return load_json(record_file, default={})

    async def validate_login(self, username: str, password: str, domain: str, save_account: bool) -> None:
        try:
            if username is None or password is None:
                raise InvalidAuth

            # Create client and login
            client = LierdaClient()
            auth_data = await client.login(username, password, domain)

            # Store auth data in config
            self.config["auth_data"] = {
                "userid": auth_data.userid,
                "username": auth_data.username,
                "domain": auth_data.domain,
                "role": auth_data.role,
                "parentid": auth_data.parentid,
                "nat": auth_data.nat,
                "phone": auth_data.phone,
            }

            if save_account:
                self._save_login_config({
                    CONF_KEY_USERNAME: username,
                    CONF_KEY_PASSWORD: password,
                    "auth_data": self.config["auth_data"],
                })

            # Close client session
            await client.close()

        except LierdaAuthError:
            if save_account:
                self._save_login_config({
                    CONF_KEY_USERNAME: username,
                    CONF_KEY_PASSWORD: password,
                })
            raise InvalidAuth
        except (LierdaConnectionError, LierdaTimeoutError):
            raise CannotConnect
        except Exception as exception:
            _LOGGER.exception("Unexpected error during login: %s", exception)
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
            # Create client and set auth data
            client = LierdaClient()

            # Manually set auth_data from stored config
            auth_data_dict = self.config["auth_data"]
            client.auth_data = AuthData(
                userid=auth_data_dict["userid"],
                username=auth_data_dict["username"],
                domain=auth_data_dict["domain"],
                role=auth_data_dict["role"],
                parentid=auth_data_dict["parentid"],
                nat=auth_data_dict["nat"],
                phone=auth_data_dict["phone"],
            )

            # Get devices
            devices = await client.get_all_devices()

            # Convert Device objects to dicts for storage
            device_list = [
                {
                    "id": device.id,
                    "name": device.name,
                    "macId": device.mac_id,
                    "ddcMac": device.ddc_mac,
                    "type": device.device_type,
                    "roomName": device.room_name,
                    "online": device.online,
                }
                for device in devices
            ]

            # Close client session
            await client.close()

            return device_list
        except (LierdaConnectionError, LierdaTimeoutError):
            raise CannotConnect
        except LierdaApiError as exception:
            _LOGGER.exception("API error while fetching devices: %s", exception)
            raise ApiError(str(exception))
        except Exception as exception:
            _LOGGER.exception("Unexpected error while fetching devices: %s", exception)
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
        unique_id = f"{self.config['auth_data']['userid']}@{LIERDA_API_LIST[user_input[CONF_LUX_DOMAIN]]}"
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

    async def async_step_init(self, user_input=None):
        """Handle options flow init."""
        # Get current refresh interval from config entry
        old_refresh_interval = self.config_entry.data.get(
            CONF_KEY_REFRESH_INTERVAL, DEFAULT_REFRESH_INTERVAL
        )
        defaults = {CONF_REFRESH_INTERVAL: old_refresh_interval}

        if user_input is not None:
            from datetime import timedelta
            refresh_interval = user_input.get(CONF_REFRESH_INTERVAL, old_refresh_interval)

            # Reload the integration to apply the new interval immediately
            # We don't need to manually update the config entry data because the options 
            # flow will return an entry which HA will save. But for the polling interval 
            # to be read by the setup, we can either store it in options or update data.
            # Here we just update the data as before.
            new_data = {**self.config_entry.data, CONF_KEY_REFRESH_INTERVAL: refresh_interval}
            self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)
            
            # The async_create_entry triggers an EVENT_OPTIONS_FLOW_FIRED but not a reload automatically.
            # However `async_reload` can restart the entry. We'll queue a reload.
            self.hass.async_create_task(
                self.hass.config_entries.async_reload(self.config_entry.entry_id)
            )

            return self.async_create_entry(title="", data={})

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
