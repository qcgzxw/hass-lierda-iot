# tests/test_binary_sensor.py
"""Tests for binary_sensor platform."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.config_entries import ConfigEntry

from custom_components.lierda_iot.models.device import Device


@pytest.mark.asyncio
class TestBinarySensorPlatform:
    """Tests for binary_sensor platform."""

    async def test_async_setup_entry_binary_sensors(self):
        """Test binary sensor platform setup."""
        from custom_components.lierda_iot.binary_sensor import async_setup_entry
        from custom_components.lierda_iot.lierda_devices import LIERDA_DEVICES

        # Create mock Home Assistant instance
        hass = MagicMock()
        hass.data = {}

        # Get a device type that has binary sensors (type 10 is door sensor with door binary sensor)
        device_type = 10
        device_config = LIERDA_DEVICES[device_type]

        # Create mock device with door attribute
        mock_device = Device(
            id=12345,
            name="Test Door Sensor",
            type=device_type,
            mac_id="AA:BB:CC:DD:EE:FF",
            attributes={"LIVE": "ON", "DOR": "OPEN", "BAT": 3.2, "_BAT": "85%"},
            available=True,
            firmware_version="1.0.0",
            ddc_id=100,
        ddc_mac="00:00:00:00:00:00",
        ddc_name="Test DDC",
        )

        # Create mock coordinator
        mock_coordinator = AsyncMock()
        mock_coordinator.data = {12345: mock_device}

        # Setup hass.data
        hass.data["lierda_iot"] = {
            "test_entry": {
                "coordinator": mock_coordinator,
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

        # Verify that binary sensor entities were created
        # Device type 10 has 1 binary sensor: door
        binary_sensor_count = sum(
            1 for config in device_config["entities"].values()
            if config["type"] == "binary_sensor"
        )
        assert len(async_add_entities.entities) == binary_sensor_count

    async def test_binary_sensor_value_updates(self):
        """Test binary sensor value updates from coordinator."""
        from custom_components.lierda_iot.binary_sensor import LierdaBinarySensor
        from custom_components.lierda_iot.coordinator import LierdaDataUpdateCoordinator

        # Create mock device
        mock_device = Device(
            id=12345,
            name="Test Door Sensor",
            type=10,
            mac_id="AA:BB:CC:DD:EE:FF",
            attributes={"DOR": "OPEN", "LIVE": "ON"},
            available=True,
            firmware_version="1.0.0",
            ddc_id=100,
        ddc_mac="00:00:00:00:00:00",
        ddc_name="Test DDC",
        )

        # Create mock coordinator
        mock_coordinator = AsyncMock(spec=LierdaDataUpdateCoordinator)
        mock_coordinator.data = {12345: mock_device}
        mock_coordinator.last_update_success = True

        # Create binary sensor config
        config = {
            "name": "Door",
            "type": "binary_sensor",
            "device_class": "door",
        }

        # Create binary sensor entity
        binary_sensor = LierdaBinarySensor(
            mock_coordinator,
            mock_device,
            "door",
            config,
        )

        # Check initial value
        assert binary_sensor.is_on is True
        assert binary_sensor.available is True

        # Update device data
        mock_device.attributes["DOR"] = "CLOSE"
        mock_coordinator.data = {12345: mock_device}

        # Check updated value
        assert binary_sensor.is_on is False
