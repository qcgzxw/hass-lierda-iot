# tests/test_sensor.py
"""Tests for sensor platform."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.config_entries import ConfigEntry

from custom_components.lierda_iot.models.device import Device


@pytest.mark.asyncio
class TestSensorPlatform:
    """Tests for sensor platform."""

    async def test_async_setup_entry_sensors(self):
        """Test sensor platform setup."""
        from custom_components.lierda_iot.sensor import async_setup_entry
        from custom_components.lierda_iot.lierda_devices import LIERDA_DEVICES

        # Create mock Home Assistant instance
        hass = MagicMock()
        hass.data = {}

        # Get a device type that has sensors (type 10 is door sensor with battery sensors)
        device_type = 10
        device_config = LIERDA_DEVICES[device_type]

        # Create mock device with battery attributes
        mock_device = Device(
            id=12345,
            name="Test Door Sensor",
            type=device_type,
            mac_id="AA:BB:CC:DD:EE:FF",
            attributes={"LIVE": "ON", "battery_voltage": 3.2, "battery_percentage": 85},
            available=True,
            firmware_version="1.0.0",
            ddc_id=100,
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

        # Verify that sensor entities were created
        # Device type 10 has 2 sensors: battery_voltage and battery_percentage
        sensor_count = sum(
            1 for config in device_config["entities"].values()
            if config["type"] == "sensor"
        )
        assert len(async_add_entities.entities) == sensor_count

    async def test_sensor_value_updates(self):
        """Test sensor value updates from coordinator."""
        from custom_components.lierda_iot.sensor import LierdaSensor
        from custom_components.lierda_iot.coordinator import LierdaDataUpdateCoordinator

        # Create mock device
        mock_device = Device(
            id=12345,
            name="Test Sensor",
            type=10,
            mac_id="AA:BB:CC:DD:EE:FF",
            attributes={"battery_voltage": 3.2, "LIVE": "ON"},
            available=True,
            firmware_version="1.0.0",
            ddc_id=100,
        )

        # Create mock coordinator
        mock_coordinator = AsyncMock(spec=LierdaDataUpdateCoordinator)
        mock_coordinator.data = {12345: mock_device}
        mock_coordinator.last_update_success = True

        # Create sensor config
        config = {
            "name": "Battery Voltage",
            "type": "sensor",
            "device_class": "voltage",
            "unit": "V",
            "state_class": "measurement",
        }

        # Create sensor entity
        sensor = LierdaSensor(
            mock_coordinator,
            mock_device,
            "battery_voltage",
            config,
        )

        # Check initial value
        assert sensor.native_value == 3.2
        assert sensor.available is True

        # Update device data
        mock_device.attributes["battery_voltage"] = 3.5
        mock_coordinator.data = {12345: mock_device}

        # Check updated value
        assert sensor.native_value == 3.5
