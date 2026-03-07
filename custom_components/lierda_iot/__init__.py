from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import LierdaClient
from .api.exceptions import LierdaApiError
from .const import (
    DOMAIN,
    PLATFORMS,
    ENTRY_VERSION,
    DEFAULT_REFRESH_INTERVAL,
    CONF_KEY_DEVICES,
    CONF_KEY_USER_AUTH_DATA,
    CONF_KEY_REFRESH_INTERVAL,
    LIERDA_LUX_URL,
)
from .coordinator import LierdaDataUpdateCoordinator
from .models.auth import AuthData

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config_entry: dict):
    _LOGGER.debug(config_entry)
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry data to new version."""
    _LOGGER.info("Migrating from version %s to %s", config_entry.version, ENTRY_VERSION)

    if config_entry.version == 1:
        # v1 -> v3: Remove devices field, rename user_auth_data -> auth_data
        new_data = {**config_entry.data}

        # Remove devices field
        if CONF_KEY_DEVICES in new_data:
            new_data.pop(CONF_KEY_DEVICES)

        # Rename user_auth_data to auth_data
        if CONF_KEY_USER_AUTH_DATA in new_data:
            new_data["auth_data"] = new_data.pop(CONF_KEY_USER_AUTH_DATA)

        # Add domain from auth_data, or use default if missing (for very old entries)
        if "auth_data" in new_data:
            if "domain" in new_data["auth_data"]:
                new_data["domain"] = new_data["auth_data"]["domain"]
            else:
                # Very old entries don't have domain - add default
                new_data["auth_data"]["domain"] = LIERDA_LUX_URL
                new_data["domain"] = LIERDA_LUX_URL

        # Update config entry
        hass.config_entries.async_update_entry(config_entry, data=new_data, version=ENTRY_VERSION)
        _LOGGER.info("Migration to version %s successful", ENTRY_VERSION)
        return True

    if config_entry.version == 2:
        # v2 -> v3: Rename user_auth_data -> auth_data
        new_data = {**config_entry.data}

        # Rename user_auth_data to auth_data
        if CONF_KEY_USER_AUTH_DATA in new_data:
            new_data["auth_data"] = new_data.pop(CONF_KEY_USER_AUTH_DATA)

        # Add domain from auth_data, or use default if missing (for very old entries)
        if "auth_data" in new_data:
            if "domain" in new_data["auth_data"]:
                new_data["domain"] = new_data["auth_data"]["domain"]
            else:
                # Very old entries don't have domain - add default
                new_data["auth_data"]["domain"] = LIERDA_LUX_URL
                new_data["domain"] = LIERDA_LUX_URL

        # Update config entry
        hass.config_entries.async_update_entry(config_entry, data=new_data, version=ENTRY_VERSION)
        _LOGGER.info("Migration to version %s successful", ENTRY_VERSION)
        return True

    # Already at the latest version
    if config_entry.version == ENTRY_VERSION:
        return True

    # Unknown version
    _LOGGER.error("Unknown config entry version: %s", config_entry.version)
    return False


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Lierda IoT from a config entry."""
    # Initialize hass.data structure
    hass.data.setdefault(DOMAIN, {})

    # Get auth data
    auth_data_dict = config_entry.data.get("auth_data", {})
    if not auth_data_dict:
        _LOGGER.error("No auth data in config entry")
        return False

    # Create auth data object
    auth_data = AuthData.from_api_response(auth_data_dict)

    # Create client
    client = LierdaClient()
    client.auth_data = auth_data

    # Create coordinator
    refresh_interval = config_entry.data.get("refresh_interval", DEFAULT_REFRESH_INTERVAL)
    coordinator = LierdaDataUpdateCoordinator(
        hass=hass,
        client=client,
        config_entry=config_entry,
        update_interval=timedelta(seconds=refresh_interval),
    )

    # Store coordinator and client
    hass.data[DOMAIN][config_entry.entry_id] = {
        "coordinator": coordinator,
        "client": client,
    }

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Forward platform setups
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

    if unload_ok:
        entry_data = hass.data[DOMAIN].get(config_entry.entry_id)
        if entry_data:
            coordinator = entry_data.get("coordinator")
            if coordinator:
                await coordinator.async_shutdown()
        hass.data[DOMAIN].pop(config_entry.entry_id, None)

    return unload_ok
