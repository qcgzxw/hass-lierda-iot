# tests/test_init.py
"""Tests for __init__ module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry, ConfigEntryState

from custom_components.lierda_iot.models.auth import AuthData


@pytest.mark.asyncio
class TestAsyncSetupEntry:
    """Tests for async_setup_entry function."""

    async def test_async_setup_entry_missing_auth_data(self):
        """Test setup fails when auth_data is missing."""
        from custom_components.lierda_iot import async_setup_entry

        # Create mock Home Assistant instance
        hass = MagicMock()
        hass.data = {}

        # Create config entry without auth_data
        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.entry_id = "test_entry"
        config_entry.domain = "lierda_iot"
        config_entry.title = "Test Entry"
        config_entry.data = {}  # Missing auth_data
        config_entry.version = 3

        with patch('custom_components.lierda_iot.api.client.LierdaClient.get_all_devices', new_callable=AsyncMock) as mock_get_devices:
            mock_get_devices.return_value = []
            # Run setup
            result = await async_setup_entry(hass, config_entry)

        # Verify setup failed
        assert result is False

    async def test_async_setup_entry_success(self):
        """Test successful setup entry."""
        from custom_components.lierda_iot import async_setup_entry

        # Create mock Home Assistant instance
        hass = MagicMock()
        hass.data = {}

        # Mock async_forward_entry_setups
        hass.config_entries = MagicMock()
        hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)

        # Create config entry with valid auth_data
        auth_data_dict = {
            "userid": 12345,
            "username": "test@example.com",
            "domain": "www.lierdalux.cn",
            "role": 1,
            "parentid": 0,
            "nat": "CN",
            "phone": "13800138000",
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.entry_id = "test_entry"
        config_entry.domain = "lierda_iot"
        config_entry.title = "Test Entry"
        config_entry.data = {
            "auth_data": auth_data_dict,
            "refresh_interval": 300,
        }
        config_entry.version = 3
        config_entry.state = ConfigEntryState.SETUP_IN_PROGRESS

        with patch('custom_components.lierda_iot.api.client.LierdaClient.get_all_devices', new_callable=AsyncMock) as mock_get_devices:
            mock_get_devices.return_value = []
            # Run setup
            result = await async_setup_entry(hass, config_entry)

        # Verify setup succeeded
        assert result is True

        # Verify hass.data structure
        assert "lierda_iot" in hass.data
        assert "test_entry" in hass.data["lierda_iot"]
        assert "coordinator" in hass.data["lierda_iot"]["test_entry"]
        assert "client" in hass.data["lierda_iot"]["test_entry"]

        # Verify async_forward_entry_setups was called
        hass.config_entries.async_forward_entry_setups.assert_called_once()

    async def test_async_setup_entry_with_default_refresh_interval(self):
        """Test setup uses default refresh interval when not specified."""
        from custom_components.lierda_iot import async_setup_entry

        # Create mock Home Assistant instance
        hass = MagicMock()
        hass.data = {}

        # Mock async_forward_entry_setups
        hass.config_entries = MagicMock()
        hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)

        # Create config entry without refresh_interval
        auth_data_dict = {
            "userid": 12345,
            "username": "test@example.com",
            "domain": "www.lierdalux.cn",
            "role": 1,
            "parentid": 0,
            "nat": "CN",
            "phone": "13800138000",
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.entry_id = "test_entry"
        config_entry.domain = "lierda_iot"
        config_entry.title = "Test Entry"
        config_entry.data = {
            "auth_data": auth_data_dict,
            # No refresh_interval specified
        }
        config_entry.version = 3
        config_entry.state = ConfigEntryState.SETUP_IN_PROGRESS

        with patch('custom_components.lierda_iot.api.client.LierdaClient.get_all_devices', new_callable=AsyncMock) as mock_get_devices:
            mock_get_devices.return_value = []
            # Run setup
            result = await async_setup_entry(hass, config_entry)

        # Verify setup succeeded
        assert result is True

        # Verify coordinator was created
        assert "coordinator" in hass.data["lierda_iot"]["test_entry"]


@pytest.mark.asyncio
class TestAsyncUnloadEntry:
    """Tests for async_unload_entry function."""

    async def test_async_unload_entry(self):
        """Test unloading config entry."""
        from custom_components.lierda_iot import async_setup_entry, async_unload_entry

        # Create mock Home Assistant instance
        hass = MagicMock()
        hass.data = {}

        # Mock config_entries
        hass.config_entries = MagicMock()
        hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
        hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

        # Create config entry with valid auth_data
        auth_data_dict = {
            "userid": 12345,
            "username": "test@example.com",
            "domain": "www.lierdalux.cn",
            "role": 1,
            "parentid": 0,
            "nat": "CN",
            "phone": "13800138000",
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.entry_id = "test_entry"
        config_entry.domain = "lierda_iot"
        config_entry.title = "Test Entry"
        config_entry.data = {
            "auth_data": auth_data_dict,
            "refresh_interval": 300,
        }
        config_entry.version = 3
        config_entry.state = ConfigEntryState.SETUP_IN_PROGRESS

        with patch('custom_components.lierda_iot.api.client.LierdaClient.get_all_devices', new_callable=AsyncMock) as mock_get_devices:
            mock_get_devices.return_value = []
            # Setup first
            await async_setup_entry(hass, config_entry)

        # Verify setup succeeded
        assert "test_entry" in hass.data["lierda_iot"]

        # Get coordinator reference and mock its async_shutdown
        coordinator = hass.data["lierda_iot"]["test_entry"]["coordinator"]
        coordinator.async_shutdown = AsyncMock()

        # Now unload
        result = await async_unload_entry(hass, config_entry)

        # Verify unload succeeded
        assert result is True
        assert "test_entry" not in hass.data["lierda_iot"]

        # Verify coordinator was shut down
        coordinator.async_shutdown.assert_called_once()

        # Verify async_unload_platforms was called
        hass.config_entries.async_unload_platforms.assert_called_once()