# tests/test_light.py
"""Tests for light platform."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.config_entries import ConfigEntry

from custom_components.lierda_iot.models.device import Device


@pytest.mark.asyncio
class TestLightPlatform:
    """Tests for light platform."""

    async def test_async_setup_entry_lights(self):
        """Test light platform setup."""
        from custom_components.lierda_iot.light import async_setup_entry
        from custom_components.lierda_iot.lierda_devices import LIERDA_DEVICES

        # Create mock Home Assistant instance
        hass = MagicMock()
        hass.data = {}

        # Get a device type that has lights (TYPE_CL_R1M is light)
        device_type = 26  # TYPE_CL_R1M
        device_config = LIERDA_DEVICES[device_type]

        # Create mock device with light attributes
        mock_device = Device(
            id=12345,
            name="Test Light",
            type=26,
            mac_id="AA:BB:CC:DD:EE:FF",
            attributes={"power": True, "brightness": 200, "LIVE": "ON"},
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

        # Verify that light entities were created
        # Device type 26 has 1 light entity
        light_count = sum(
            1 for config in device_config["entities"].values()
            if config["type"] == "light"
        )
        assert len(async_add_entities.entities) == light_count

    async def test_light_control(self):
        """Test light turn_on and turn_off."""
        from custom_components.lierda_iot.light import LierdaLight

        # Create mock device
        mock_device = Device(
            id=12345,
            name="Test Light",
            type=26,
            mac_id="AA:BB:CC:DD:EE:FF",
            attributes={"power": "OFF", "brightness": 100, "LIVE": "ON"},
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

        # Create light entity
        light = LierdaLight(
            mock_coordinator,
            mock_device,
            "light",
            {"type": "light", "icon": "mdi:lightbulb"},
            mock_client,
        )

        # Check initial state
        assert light.is_on is False

        # Turn on
        await light.async_turn_on()
        mock_client.set_device_attribute.assert_called()

        # Turn off
        await light.async_turn_off()
        assert mock_client.set_device_attribute.call_count == 2