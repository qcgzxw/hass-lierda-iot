# tests/test_cover.py
"""Tests for cover platform."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.config_entries import ConfigEntry

from custom_components.lierda_iot.models.device import Device


@pytest.mark.asyncio
class TestCoverPlatform:
    """Tests for cover platform."""

    async def test_async_setup_entry_covers(self):
        """Test cover platform setup."""
        from custom_components.lierda_iot.cover import async_setup_entry
        from custom_components.lierda_iot.lierda_devices import LIERDA_DEVICES

        # Create mock Home Assistant instance
        hass = MagicMock()
        hass.data = {}

        # Get a device type that has covers (TYPE_WD_RXJ is curtain)
        device_type = 5  # TYPE_WD_RXJ
        device_config = LIERDA_DEVICES[device_type]

        # Create mock device with cover attributes
        mock_device = Device(
            id=12345,
            name="Test Curtain",
            type=5,
            mac_id="AA:BB:CC:DD:EE:FF",
            attributes={"WIN": "STOP", "LEV": 50, "LIVE": "ON"},
            available=True,
            firmware_version="1.0.0",
            ddc_id=100,
        ddc_mac="00:00:00:00:00:00",
        ddc_name="Test DDC",
        )

        # Create mock coordinator
        mock_coordinator = AsyncMock()
        mock_coordinator.data = {12345: mock_device}

        # Create mock client
        mock_client = AsyncMock()

        # Setup hass.data
        hass.data["lierda_iot"] = {
            "test_entry": {
                "coordinator": mock_coordinator,
                "client": mock_client,
            }
        }

        # Create mock add_entities callback
        def async_add_entities(entities):
            """Mock async_add_entities that captures entities."""
            async_add_entities.entities = entities

        async_add_entities.entities = []

        # Create mock config entry
        config_entry = MagicMock(spec=ConfigEntry)
        config_entry.entry_id = "test_entry"
        config_entry.domain = "lierda_iot"
        config_entry.title = "Test Entry"
        config_entry.data = {}
        config_entry.version = 3

        # Call setup
        await async_setup_entry(hass, config_entry, async_add_entities)

        # Verify entities were added
        assert len(async_add_entities.entities) > 0

        # Verify that cover entities were created
        # Device type 5 has 1 cover entity
        cover_count = sum(
            1 for config in device_config["entities"].values()
            if config["type"] == "cover"
        )
        assert len(async_add_entities.entities) == cover_count

    async def test_cover_control(self):
        """Test cover open, close, and set_position."""
        from custom_components.lierda_iot.cover import LierdaCover

        # Create mock device
        mock_device = Device(
            id=12345,
            name="Test Curtain",
            type=5,
            mac_id="AA:BB:CC:DD:EE:FF",
            attributes={"WIN": "STOP", "LEV": 50, "LIVE": "ON"},
            available=True,
            firmware_version="1.0.0",
            ddc_id=100,
        ddc_mac="00:00:00:00:00:00",
        ddc_name="Test DDC",
        )

        # Create mock coordinator and client
        mock_coordinator = AsyncMock()
        mock_coordinator.data = {12345: mock_device}
        mock_coordinator.last_update_success = True

        mock_client = AsyncMock()

        # Create cover entity
        cover = LierdaCover(
            mock_coordinator,
            mock_device,
            "curtain",
            {"type": "cover", "icon": "mdi:curtains"},
            mock_client,
        )

        # Check initial state (STOP means unknown state)
        assert cover.is_closed is None
        assert cover.current_cover_position == 50

        # Open cover
        await cover.async_open_cover()
        mock_client.set_device_attribute.assert_called()

        # Close cover
        await cover.async_close_cover()
        assert mock_client.set_device_attribute.call_count == 2

        # Set position
        await cover.async_set_cover_position(position=75)
        assert mock_client.set_device_attribute.call_count == 3

    async def test_cover_is_closed_property(self):
        """Test cover is_closed property with different states."""
        from custom_components.lierda_iot.cover import LierdaCover

        # Test when window is OPEN
        mock_device = Device(
            id=12345,
            name="Test Curtain",
            type=5,
            mac_id="AA:BB:CC:DD:EE:FF",
            attributes={"WIN": "OPEN", "LEV": 100, "LIVE": "ON"},
            available=True,
            firmware_version="1.0.0",
            ddc_id=100,
        ddc_mac="00:00:00:00:00:00",
        ddc_name="Test DDC",
        )

        mock_coordinator = AsyncMock()
        mock_coordinator.data = {12345: mock_device}
        mock_coordinator.last_update_success = True

        mock_client = AsyncMock()

        cover = LierdaCover(
            mock_coordinator,
            mock_device,
            "curtain",
            {"type": "cover", "icon": "mdi:curtains"},
            mock_client,
        )

        assert cover.is_closed is False

        # Test when window is CLOSE
        mock_device.attributes = {"WIN": "CLOSE", "LEV": 0, "LIVE": "ON"}
        assert cover.is_closed is True

        # Test when window is STOP
        mock_device.attributes = {"WIN": "STOP", "LEV": 50, "LIVE": "ON"}
        assert cover.is_closed is None

    async def test_cover_position_property(self):
        """Test cover current_cover_position property."""
        from custom_components.lierda_iot.cover import LierdaCover

        mock_device = Device(
            id=12345,
            name="Test Curtain",
            type=5,
            mac_id="AA:BB:CC:DD:EE:FF",
            attributes={"WIN": "STOP", "LEV": 75, "LIVE": "ON"},
            available=True,
            firmware_version="1.0.0",
            ddc_id=100,
        ddc_mac="00:00:00:00:00:00",
        ddc_name="Test DDC",
        )

        mock_coordinator = AsyncMock()
        mock_coordinator.data = {12345: mock_device}
        mock_coordinator.last_update_success = True

        mock_client = AsyncMock()

        cover = LierdaCover(
            mock_coordinator,
            mock_device,
            "curtain",
            {"type": "cover", "icon": "mdi:curtains"},
            mock_client,
        )

        assert cover.current_cover_position == 75

        # Test with None level
        mock_device.attributes = {"WIN": "STOP", "LIVE": "ON"}
        assert cover.current_cover_position is None