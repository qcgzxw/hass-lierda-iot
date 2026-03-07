# tests/test_config_flow.py
"""Tests for Lierda config flow and migration."""

from unittest.mock import MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry

from custom_components.lierda_iot import async_migrate_entry
from custom_components.lierda_iot.const import (
    CONF_KEY_DEVICES,
    CONF_KEY_REFRESH_INTERVAL,
    CONF_KEY_USER_AUTH_DATA,
    ENTRY_VERSION,
)


@pytest.mark.asyncio
class TestConfigMigration:
    """Tests for config entry migration."""

    async def test_v1_to_v3_migration_removes_devices_field(self):
        """Test v1 to v3 migration removes devices field."""
        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create v1 config entry with devices
        v1_data = {
            "user_auth_data": {
                "userid": "12345",
                "username": "test@example.com",
                "token": "abc123",
                "domain": "www.lierdalux.cn",
            },
            "devices": {
                "1": {"id": "1", "name": "Light 1"},
                "2": {"id": "2", "name": "Light 2"},
            },
            "refresh_interval": 300,
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.version = 1
        config_entry.data = v1_data

        # Mock async_update_entry
        updated_data = {}

        def mock_update_entry(entry, data=None, version=None):
            nonlocal updated_data
            if data:
                updated_data = data
            if version:
                entry.version = version

        hass.config_entries.async_update_entry = mock_update_entry

        # Run migration
        result = await async_migrate_entry(hass, config_entry)

        # Verify migration succeeded
        assert result is True
        assert config_entry.version == ENTRY_VERSION
        assert "devices" not in updated_data

    async def test_v1_to_v3_migration_renames_user_auth_data(self):
        """Test v1 to v3 migration renames user_auth_data to auth_data."""
        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create v1 config entry
        v1_data = {
            "user_auth_data": {
                "userid": "12345",
                "username": "test@example.com",
                "token": "abc123",
                "domain": "www.lierdalux.cn",
            },
            "devices": {},
            "refresh_interval": 300,
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.version = 1
        config_entry.data = v1_data

        # Mock async_update_entry
        updated_data = {}

        def mock_update_entry(entry, data=None, version=None):
            nonlocal updated_data
            if data:
                updated_data = data
            if version:
                entry.version = version

        hass.config_entries.async_update_entry = mock_update_entry

        # Run migration
        result = await async_migrate_entry(hass, config_entry)

        # Verify migration succeeded
        assert result is True
        assert config_entry.version == ENTRY_VERSION
        assert "auth_data" in updated_data
        assert "user_auth_data" not in updated_data
        assert updated_data["auth_data"]["userid"] == "12345"
        assert updated_data["auth_data"]["username"] == "test@example.com"
        assert updated_data["auth_data"]["token"] == "abc123"

    async def test_v1_to_v3_migration_adds_domain_from_auth_data(self):
        """Test v1 to v3 migration adds domain field from auth_data."""
        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create v1 config entry
        v1_data = {
            "user_auth_data": {
                "userid": "12345",
                "username": "test@example.com",
                "token": "abc123",
                "domain": "www.lierdalux.cn",
            },
            "devices": {},
            "refresh_interval": 300,
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.version = 1
        config_entry.data = v1_data

        # Mock async_update_entry
        updated_data = {}

        def mock_update_entry(entry, data=None, version=None):
            nonlocal updated_data
            if data:
                updated_data = data
            if version:
                entry.version = version

        hass.config_entries.async_update_entry = mock_update_entry

        # Run migration
        result = await async_migrate_entry(hass, config_entry)

        # Verify migration succeeded
        assert result is True
        assert config_entry.version == ENTRY_VERSION
        assert "domain" in updated_data
        assert updated_data["domain"] == "www.lierdalux.cn"

    async def test_v1_to_v3_migration_preserves_refresh_interval(self):
        """Test v1 to v3 migration preserves refresh_interval."""
        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create v1 config entry with custom refresh interval
        v1_data = {
            "user_auth_data": {
                "userid": "12345",
                "username": "test@example.com",
                "token": "abc123",
                "domain": "www.lierdalux.cn",
            },
            "devices": {},
            "refresh_interval": 600,
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.version = 1
        config_entry.data = v1_data

        # Mock async_update_entry
        updated_data = {}

        def mock_update_entry(entry, data=None, version=None):
            nonlocal updated_data
            if data:
                updated_data = data
            if version:
                entry.version = version

        hass.config_entries.async_update_entry = mock_update_entry

        # Run migration
        result = await async_migrate_entry(hass, config_entry)

        # Verify migration succeeded
        assert result is True
        assert config_entry.version == ENTRY_VERSION
        assert "refresh_interval" in updated_data
        assert updated_data["refresh_interval"] == 600

    async def test_v2_to_v3_migration_renames_user_auth_data(self):
        """Test v2 to v3 migration renames user_auth_data to auth_data."""
        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create v2 config entry
        v2_data = {
            "user_auth_data": {
                "userid": "67890",
                "username": "user@example.com",
                "token": "xyz789",
                "domain": "lsd.lierdalux.cn",
            },
            "refresh_interval": 300,
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.version = 2
        config_entry.data = v2_data

        # Mock async_update_entry
        updated_data = {}

        def mock_update_entry(entry, data=None, version=None):
            nonlocal updated_data
            if data:
                updated_data = data
            if version:
                entry.version = version

        hass.config_entries.async_update_entry = mock_update_entry

        # Run migration
        result = await async_migrate_entry(hass, config_entry)

        # Verify migration succeeded
        assert result is True
        assert config_entry.version == ENTRY_VERSION
        assert "auth_data" in updated_data
        assert "user_auth_data" not in updated_data
        assert updated_data["auth_data"]["userid"] == "67890"
        assert updated_data["auth_data"]["username"] == "user@example.com"
        assert updated_data["auth_data"]["token"] == "xyz789"

    async def test_v2_to_v3_migration_adds_domain_from_auth_data(self):
        """Test v2 to v3 migration adds domain field from auth_data."""
        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create v2 config entry
        v2_data = {
            "user_auth_data": {
                "userid": "67890",
                "username": "user@example.com",
                "token": "xyz789",
                "domain": "hotel.lierdalux.cn",
            },
            "refresh_interval": 300,
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.version = 2
        config_entry.data = v2_data

        # Mock async_update_entry
        updated_data = {}

        def mock_update_entry(entry, data=None, version=None):
            nonlocal updated_data
            if data:
                updated_data = data
            if version:
                entry.version = version

        hass.config_entries.async_update_entry = mock_update_entry

        # Run migration
        result = await async_migrate_entry(hass, config_entry)

        # Verify migration succeeded
        assert result is True
        assert config_entry.version == ENTRY_VERSION
        assert "domain" in updated_data
        assert updated_data["domain"] == "hotel.lierdalux.cn"

    async def test_v2_to_v3_migration_preserves_refresh_interval(self):
        """Test v2 to v3 migration preserves refresh_interval."""
        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create v2 config entry with custom refresh interval
        v2_data = {
            "user_auth_data": {
                "userid": "67890",
                "username": "user@example.com",
                "token": "xyz789",
                "domain": "www.lierdalux.cn",
            },
            "refresh_interval": 900,
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.version = 2
        config_entry.data = v2_data

        # Mock async_update_entry
        updated_data = {}

        def mock_update_entry(entry, data=None, version=None):
            nonlocal updated_data
            if data:
                updated_data = data
            if version:
                entry.version = version

        hass.config_entries.async_update_entry = mock_update_entry

        # Run migration
        result = await async_migrate_entry(hass, config_entry)

        # Verify migration succeeded
        assert result is True
        assert config_entry.version == ENTRY_VERSION
        assert "refresh_interval" in updated_data
        assert updated_data["refresh_interval"] == 900

    async def test_v3_config_returns_true_without_changes(self):
        """Test v3 config entry returns True without changes."""
        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create v3 config entry
        v3_data = {
            "auth_data": {
                "userid": "99999",
                "username": "v3@example.com",
                "token": "v3token",
                "domain": "www.lierdalux.cn",
            },
            "refresh_interval": 300,
            "domain": "www.lierdalux.cn",
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.version = ENTRY_VERSION
        config_entry.data = v3_data

        # Run migration
        result = await async_migrate_entry(hass, config_entry)

        # Verify migration succeeded without changes
        assert result is True
        assert config_entry.version == ENTRY_VERSION

    async def test_v1_migration_preserves_auth_data_content(self):
        """Test v1 migration preserves all auth_data content."""
        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create v1 config entry with full auth data
        v1_data = {
            "user_auth_data": {
                "userid": "11111",
                "username": "full@example.com",
                "token": "fulltoken123",
                "domain": "www.lierdalux.cn",
                "extra_field": "extra_value",
                "another_field": 42,
            },
            "devices": {},
            "refresh_interval": 450,
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.version = 1
        config_entry.data = v1_data

        # Mock async_update_entry
        updated_data = {}

        def mock_update_entry(entry, data=None, version=None):
            nonlocal updated_data
            if data:
                updated_data = data
            if version:
                entry.version = version

        hass.config_entries.async_update_entry = mock_update_entry

        # Run migration
        result = await async_migrate_entry(hass, config_entry)

        # Verify all auth data is preserved
        assert result is True
        assert updated_data["auth_data"]["userid"] == "11111"
        assert updated_data["auth_data"]["username"] == "full@example.com"
        assert updated_data["auth_data"]["token"] == "fulltoken123"
        assert updated_data["auth_data"]["domain"] == "www.lierdalux.cn"
        assert updated_data["auth_data"]["extra_field"] == "extra_value"
        assert updated_data["auth_data"]["another_field"] == 42

    async def test_v2_migration_preserves_auth_data_content(self):
        """Test v2 migration preserves all auth_data content."""
        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create v2 config entry with full auth data
        v2_data = {
            "user_auth_data": {
                "userid": "22222",
                "username": "v2full@example.com",
                "token": "v2token456",
                "domain": "lsd.lierdalux.cn",
                "custom_field": "custom_value",
                "numeric_field": 123,
            },
            "refresh_interval": 750,
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.version = 2
        config_entry.data = v2_data

        # Mock async_update_entry
        updated_data = {}

        def mock_update_entry(entry, data=None, version=None):
            nonlocal updated_data
            if data:
                updated_data = data
            if version:
                entry.version = version

        hass.config_entries.async_update_entry = mock_update_entry

        # Run migration
        result = await async_migrate_entry(hass, config_entry)

        # Verify all auth data is preserved
        assert result is True
        assert updated_data["auth_data"]["userid"] == "22222"
        assert updated_data["auth_data"]["username"] == "v2full@example.com"
        assert updated_data["auth_data"]["token"] == "v2token456"
        assert updated_data["auth_data"]["domain"] == "lsd.lierdalux.cn"
        assert updated_data["auth_data"]["custom_field"] == "custom_value"
        assert updated_data["auth_data"]["numeric_field"] == 123

    async def test_v1_migration_handles_missing_optional_fields(self):
        """Test v1 migration handles missing optional fields gracefully."""
        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create v1 config entry without optional fields
        v1_data = {
            "user_auth_data": {
                "userid": "33333",
                "token": "minimal_token",
            },
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.version = 1
        config_entry.data = v1_data

        # Mock async_update_entry
        updated_data = {}

        def mock_update_entry(entry, data=None, version=None):
            nonlocal updated_data
            if data:
                updated_data = data
            if version:
                entry.version = version

        hass.config_entries.async_update_entry = mock_update_entry

        # Run migration
        result = await async_migrate_entry(hass, config_entry)

        # Verify migration succeeded
        assert result is True
        assert "auth_data" in updated_data
        assert updated_data["auth_data"]["userid"] == "33333"
        assert updated_data["auth_data"]["token"] == "minimal_token"

    async def test_v2_migration_handles_missing_optional_fields(self):
        """Test v2 migration handles missing optional fields gracefully."""
        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create v2 config entry without optional fields
        v2_data = {
            "user_auth_data": {
                "userid": "44444",
                "token": "minimal_v2_token",
            },
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.version = 2
        config_entry.data = v2_data

        # Mock async_update_entry
        updated_data = {}

        def mock_update_entry(entry, data=None, version=None):
            nonlocal updated_data
            if data:
                updated_data = data
            if version:
                entry.version = version

        hass.config_entries.async_update_entry = mock_update_entry

        # Run migration
        result = await async_migrate_entry(hass, config_entry)

        # Verify migration succeeded
        assert result is True
        assert "auth_data" in updated_data
        assert updated_data["auth_data"]["userid"] == "44444"
        assert updated_data["auth_data"]["token"] == "minimal_v2_token"

    async def test_unknown_version_returns_false(self):
        """Test unknown config entry version returns False."""
        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create config entry with unknown version
        unknown_data = {
            "auth_data": {
                "userid": "55555",
            },
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.version = 99
        config_entry.data = unknown_data

        # Run migration
        result = await async_migrate_entry(hass, config_entry)

        # Verify migration failed
        assert result is False

    async def test_v1_migration_complete_structure(self):
        """Test v1 to v3 migration produces complete v3 structure."""
        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create v1 config entry
        v1_data = {
            "user_auth_data": {
                "userid": "66666",
                "username": "complete@example.com",
                "token": "complete_token",
                "domain": "hotel.lierdalux.cn",
            },
            "devices": {
                "1": {"id": "1", "name": "Device 1"},
                "2": {"id": "2", "name": "Device 2"},
            },
            "refresh_interval": 500,
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.version = 1
        config_entry.data = v1_data

        # Mock async_update_entry
        updated_data = {}

        def mock_update_entry(entry, data=None, version=None):
            nonlocal updated_data
            if data:
                updated_data = data
            if version:
                entry.version = version

        hass.config_entries.async_update_entry = mock_update_entry

        # Run migration
        result = await async_migrate_entry(hass, config_entry)

        # Verify complete v3 structure
        assert result is True
        assert config_entry.version == ENTRY_VERSION

        # Check v3 structure
        assert "auth_data" in updated_data
        assert "refresh_interval" in updated_data
        assert "domain" in updated_data
        assert "user_auth_data" not in updated_data
        assert "devices" not in updated_data

        # Check values
        assert updated_data["auth_data"]["userid"] == "66666"
        assert updated_data["refresh_interval"] == 500
        assert updated_data["domain"] == "hotel.lierdalux.cn"

    async def test_v2_migration_complete_structure(self):
        """Test v2 to v3 migration produces complete v3 structure."""
        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create v2 config entry
        v2_data = {
            "user_auth_data": {
                "userid": "77777",
                "username": "v2complete@example.com",
                "token": "v2_complete_token",
                "domain": "www.lierdalux.cn",
            },
            "refresh_interval": 400,
        }

        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.version = 2
        config_entry.data = v2_data

        # Mock async_update_entry
        updated_data = {}

        def mock_update_entry(entry, data=None, version=None):
            nonlocal updated_data
            if data:
                updated_data = data
            if version:
                entry.version = version

        hass.config_entries.async_update_entry = mock_update_entry

        # Run migration
        result = await async_migrate_entry(hass, config_entry)

        # Verify complete v3 structure
        assert result is True
        assert config_entry.version == ENTRY_VERSION

        # Check v3 structure
        assert "auth_data" in updated_data
        assert "refresh_interval" in updated_data
        assert "domain" in updated_data
        assert "user_auth_data" not in updated_data

        # Check values
        assert updated_data["auth_data"]["userid"] == "77777"
        assert updated_data["refresh_interval"] == 400
        assert updated_data["domain"] == "www.lierdalux.cn"