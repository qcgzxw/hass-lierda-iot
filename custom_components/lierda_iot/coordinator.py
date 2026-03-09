# custom_components/lierda_iot/coordinator.py
"""DataUpdateCoordinator for Lierda IoT integration."""

import logging
import os
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api.client import LierdaClient
from .api.exceptions import LierdaApiError, LierdaAuthError, LierdaConnectionError, LierdaTimeoutError
from .const import DOMAIN, CONF_KEY_USERNAME, CONF_KEY_PASSWORD
from .models.device import Device

try:
    from homeassistant.util.json import load_json
except ImportError:
    import json
    def load_json(path, default=None):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception:
            return default if default is not None else {}

_LOGGER = logging.getLogger(__name__)


class LierdaDataUpdateCoordinator(DataUpdateCoordinator[dict[int, Device]]):
    """Coordinator to manage data updates from Lierda IoT API."""

    STORAGE_PATH = f".storage/{DOMAIN}"

    def __init__(
        self,
        hass: HomeAssistant,
        client: LierdaClient,
        update_interval: timedelta,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance
            client: Lierda API client instance
            config_entry: Config entry instance
            update_interval: How often to update data
        """
        super().__init__(
            hass,
            _LOGGER,
            name="Lierda IoT",
            update_interval=update_interval,
            config_entry=config_entry,
        )
        self.client = client
        self.config_entry = config_entry
        self._reauth_attempted = False  # Flag to prevent multiple reauth attempts per cycle

    def _load_saved_credentials(self) -> dict[str, str] | None:
        """Load saved credentials from storage.

        Returns:
            Dictionary with username and password, or None if not found
        """
        try:
            record_file = self.hass.config.path(f"{self.STORAGE_PATH}/login.json")
            login_data = load_json(record_file, default={})
            if login_data and CONF_KEY_USERNAME in login_data and CONF_KEY_PASSWORD in login_data:
                return {
                    "username": login_data[CONF_KEY_USERNAME],
                    "password": login_data[CONF_KEY_PASSWORD],
                }
        except Exception as err:
            _LOGGER.warning("Failed to load saved credentials: %s", err)
        return None

    def _is_auth_error(self, error_message: str) -> bool:
        """Check if an error message indicates an authentication failure.

        Args:
            error_message: Error message from API

        Returns:
            True if this is an authentication error
        """
        auth_error_keywords = [
            "用户失效",
            "请重新登录",
            "登录失效",
            "认证失败",
            "未授权",
            "unauthorized",
            "authentication failed",
        ]
        error_lower = error_message.lower()
        return any(keyword.lower() in error_lower for keyword in auth_error_keywords)

    async def _attempt_reauth(self) -> bool:
        """Attempt to re-authenticate using saved credentials.

        Returns:
            True if re-authentication was successful
        """
        # Load saved credentials
        credentials = self._load_saved_credentials()
        if not credentials:
            _LOGGER.warning("No saved credentials found for re-authentication")
            return False

        try:
            _LOGGER.info("Attempting to re-authenticate with saved credentials")
            # Get domain from current auth_data
            domain = self.client.auth_data.domain if self.client.auth_data else "www.lierdalux.cn"

            # Attempt login
            new_auth_data = await self.client.login(
                credentials["username"],
                credentials["password"],
                domain
            )

            _LOGGER.info("Re-authentication successful for user %s", new_auth_data.username)

            # Update config entry with new auth_data (including new nat)
            new_data = {**self.config_entry.data}
            new_data["auth_data"] = {
                "userid": new_auth_data.userid,
                "username": new_auth_data.username,
                "domain": new_auth_data.domain,
                "role": new_auth_data.role,
                "parentid": new_auth_data.parentid,
                "nat": new_auth_data.nat,
                "phone": new_auth_data.phone,
            }

            # Update the config entry
            self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)
            _LOGGER.info("Updated config entry with new auth_data (nat: %s)", new_auth_data.nat)

            return True

        except (LierdaAuthError, LierdaConnectionError, LierdaTimeoutError) as err:
            _LOGGER.error("Re-authentication failed: %s", err)
            return False
        except Exception as err:
            _LOGGER.error("Unexpected error during re-authentication: %s", err)
            return False

    async def _async_update_data(self) -> dict[int, Device]:
        """Fetch all devices from API.

        Returns:
            Dictionary of devices keyed by device ID

        Raises:
            UpdateFailed: If API request fails
        """
        from .lierda_devices import LIERDA_DEVICES

        try:
            # Fetch all devices from API
            all_devices = await self.client.get_all_devices()

            device_dict = {}
            for device in all_devices:
                # Skip virtual/placeholder devices
                if device.mac_id == "0000000000000000":
                    _LOGGER.debug("Skipping virtual device %s (%s)", device.name, device.id)
                    continue

                # Check if device type is supported
                if device.type not in LIERDA_DEVICES:
                    # Only log once per fetch, rather than in every platform
                    _LOGGER.debug("Unknown or unsupported device type %s for device %s", device.type, device.id)
                    continue

                device_dict[device.id] = device

            _LOGGER.debug("Updated %d devices", len(device_dict))

            # Reset reauth flag on successful update
            self._reauth_attempted = False

            return device_dict

        except LierdaApiError as err:
            error_message = str(err)

            # Check if this is an authentication error
            if self._is_auth_error(error_message):
                _LOGGER.warning("Authentication error detected: %s", error_message)

                # Only attempt reauth once per update cycle
                if not self._reauth_attempted:
                    _LOGGER.info("Attempting automatic re-authentication")
                    self._reauth_attempted = True

                    # Try to re-authenticate
                    if await self._attempt_reauth():
                        # Retry fetching devices after successful reauth
                        try:
                            _LOGGER.info("Re-authentication successful, retrying device fetch")
                            all_devices = await self.client.get_all_devices()

                            device_dict = {}
                            for device in all_devices:
                                # Skip virtual/placeholder devices
                                if device.mac_id == "0000000000000000":
                                    _LOGGER.debug("Skipping virtual device %s (%s)", device.name, device.id)
                                    continue

                                # Check if device type is supported
                                if device.type not in LIERDA_DEVICES:
                                    _LOGGER.debug("Unknown or unsupported device type %s for device %s", device.type, device.id)
                                    continue

                                device_dict[device.id] = device

                            _LOGGER.info("Successfully updated %d devices after re-authentication", len(device_dict))
                            return device_dict

                        except LierdaApiError as retry_err:
                            _LOGGER.error("Failed to fetch devices after re-authentication: %s", retry_err)
                            # Fall through to raise UpdateFailed
                    else:
                        _LOGGER.error("Automatic re-authentication failed")
                else:
                    _LOGGER.warning("Re-authentication already attempted in this cycle, skipping")

            # Wrap LierdaApiError in UpdateFailed for HA coordinator
            _LOGGER.error("Failed to update devices: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err
