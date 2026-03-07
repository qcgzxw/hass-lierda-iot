# tests/test_switch.py
"""Tests for switch platform."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.config_entries import ConfigEntry

from custom_components.lierda_iot.models.device import Device


@pytest.mark.asyncio
class TestSwitchPlatform:
    """Tests for switch platform."""

    async def test_async_setup_entry_switches(self):
        """Test switch platform setup."""
        from custom_components.lierda_iot.switch import async_setup_entry
        from custom_components.lierda_iot.lierda_devices import LIERDA_DEVICES

        # Create mock Home Assistant instance
        hass = MagicMock()
        hass.data = {}

        # Get a device type that has switches (TYPE_SW_KY1 has 1 switch)
        device_type = 53  # TYPE_SW_KY1
        device_config = LIERDA_DEVICES[device_type]

        # Create mock device with switch attributes (power without brightness)
        mock_device = Device(
            id=12345,
            name="Test Switch",
            type=53,
            mac_id="AA:BB:CC:DD:EE:FF",
            attributes={"SWI": "0x01", "KY1": "ON", "LIVE": "ON"},
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

        # Verify that switch entities were created
        # Device type 53 has 1 switch entity
        switch_count = sum(
            1 for config in device_config["entities"].values()
            if config["type"] == "switch"
        )
        assert len(async_add_entities.entities) == switch_count

    async def test_switch_control(self):
        """Test switch turn_on and turn_off."""
        from custom_components.lierda_iot.switch import LierdaSwitch

        # Create mock device
        mock_device = Device(
            id=12345,
            name="Test Switch",
            type=53,
            mac_id="AA:BB:CC:DD:EE:FF",
            attributes={"SWI": "0x00", "KY1": "OFF", "LIVE": "ON"},
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

        # Create switch entity
        switch = LierdaSwitch(
            mock_coordinator,
            mock_device,
            "ky1",
            {"type": "switch", "name": "开关1"},
            mock_client,
        )

        # Check initial state
        assert switch.is_on is False

        # Turn on
        await switch.async_turn_on()
        mock_client.set_device_attribute.assert_called_with(
            12345, "AA:BB:CC:DD:EE:FF", "00:00:00:00:00:00", "KY1", "ON"
        )

        # Turn off
        await switch.async_turn_off()
        assert mock_client.set_device_attribute.call_count == 2