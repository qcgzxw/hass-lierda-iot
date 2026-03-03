# tests/test_coordinator.py
"""Tests for Lierda DataUpdateCoordinator."""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.lierda_iot.api.exceptions import LierdaApiError
from custom_components.lierda_iot.models.device import Device


@pytest.mark.asyncio
class TestLierdaDataUpdateCoordinator:
    """Tests for LierdaDataUpdateCoordinator."""

    async def test_successful_update_returns_device_dict(self):
        """Test successful update returns device dictionary keyed by ID."""
        from custom_components.lierda_iot.coordinator import LierdaDataUpdateCoordinator

        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create mock client with authenticated user
        client = MagicMock()
        client.auth_data = MagicMock()  # Simulate authenticated user

        # Create mock devices
        device1 = Device(
            id=1,
            name="Living Room Light",
            type=1,
            mac_id="AA:BB:CC:DD:EE:FF",
            attributes={"LIVE": "ON", "POWER": "ON"},
            available=True,
            firmware_version="1.0.0",
            ddc_id=100,
        )
        device2 = Device(
            id=2,
            name="Bedroom Light",
            type=1,
            mac_id="11:22:33:44:55:66",
            attributes={"LIVE": "ON", "POWER": "OFF"},
            available=True,
            firmware_version="1.0.1",
            ddc_id=101,
        )

        # Mock get_all_devices to return list of devices
        client.get_all_devices = AsyncMock(return_value=[device1, device2])

        # Create coordinator
        update_interval = timedelta(seconds=30)
        coordinator = LierdaDataUpdateCoordinator(
            hass=hass,
            client=client,
            update_interval=update_interval,
        )

        # Call _async_update_data
        result = await coordinator._async_update_data()

        # Verify result is a dict keyed by device ID
        assert isinstance(result, dict)
        assert len(result) == 2
        assert result[1] == device1
        assert result[2] == device2

        # Verify client method was called
        client.get_all_devices.assert_called_once()

    async def test_empty_device_list_returns_empty_dict(self):
        """Test empty device list returns empty dictionary."""
        from custom_components.lierda_iot.coordinator import LierdaDataUpdateCoordinator

        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create mock client
        client = MagicMock()
        client.auth_data = MagicMock()

        # Mock get_all_devices to return empty list
        client.get_all_devices = AsyncMock(return_value=[])

        # Create coordinator
        update_interval = timedelta(seconds=30)
        coordinator = LierdaDataUpdateCoordinator(
            hass=hass,
            client=client,
            update_interval=update_interval,
        )

        # Call _async_update_data
        result = await coordinator._async_update_data()

        # Verify result is an empty dict
        assert isinstance(result, dict)
        assert len(result) == 0
        assert result == {}

        # Verify client method was called
        client.get_all_devices.assert_called_once()

    async def test_api_error_raises_update_failed(self):
        """Test LierdaApiError raises UpdateFailed exception."""
        from custom_components.lierda_iot.coordinator import LierdaDataUpdateCoordinator

        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create mock client
        client = MagicMock()
        client.auth_data = MagicMock()

        # Mock get_all_devices to raise LierdaApiError
        client.get_all_devices = AsyncMock(
            side_effect=LierdaApiError("Failed to retrieve devices")
        )

        # Create coordinator
        update_interval = timedelta(seconds=30)
        coordinator = LierdaDataUpdateCoordinator(
            hass=hass,
            client=client,
            update_interval=update_interval,
        )

        # Call _async_update_data and expect UpdateFailed
        with pytest.raises(UpdateFailed) as exc_info:
            await coordinator._async_update_data()

        # Verify error message contains original error
        assert "Failed to retrieve devices" in str(exc_info.value)

        # Verify client method was called
        client.get_all_devices.assert_called_once()

    async def test_correct_update_interval_set(self):
        """Test coordinator has correct update interval."""
        from custom_components.lierda_iot.coordinator import LierdaDataUpdateCoordinator

        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create mock client
        client = MagicMock()

        # Create coordinator with specific update interval
        update_interval = timedelta(minutes=5)
        coordinator = LierdaDataUpdateCoordinator(
            hass=hass,
            client=client,
            update_interval=update_interval,
        )

        # Verify update interval is set correctly
        assert coordinator.update_interval == update_interval
        assert coordinator.update_interval == timedelta(minutes=5)

    async def test_data_format_is_dict_keyed_by_id(self):
        """Test data format is dict[int, Device] keyed by device ID."""
        from custom_components.lierda_iot.coordinator import LierdaDataUpdateCoordinator

        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create mock client
        client = MagicMock()
        client.auth_data = MagicMock()

        # Create devices with different IDs
        devices = [
            Device(
                id=100,
                name="Device 100",
                type=1,
                mac_id="MAC1",
                attributes={},
                available=True,
                firmware_version=None,
                ddc_id=1,
            ),
            Device(
                id=200,
                name="Device 200",
                type=2,
                mac_id="MAC2",
                attributes={},
                available=True,
                firmware_version=None,
                ddc_id=2,
            ),
            Device(
                id=300,
                name="Device 300",
                type=3,
                mac_id="MAC3",
                attributes={},
                available=True,
                firmware_version=None,
                ddc_id=3,
            ),
        ]

        # Mock get_all_devices
        client.get_all_devices = AsyncMock(return_value=devices)

        # Create coordinator
        coordinator = LierdaDataUpdateCoordinator(
            hass=hass,
            client=client,
            update_interval=timedelta(seconds=30),
        )

        # Call _async_update_data
        result = await coordinator._async_update_data()

        # Verify all keys are integers
        assert all(isinstance(key, int) for key in result.keys())

        # Verify all values are Device instances
        assert all(isinstance(value, Device) for value in result.values())

        # Verify correct mapping
        assert result[100].name == "Device 100"
        assert result[200].name == "Device 200"
        assert result[300].name == "Device 300"

    async def test_coordinator_extends_data_update_coordinator(self):
        """Test LierdaDataUpdateCoordinator extends DataUpdateCoordinator."""
        from custom_components.lierda_iot.coordinator import LierdaDataUpdateCoordinator

        # Create mock instances
        hass = MagicMock()
        client = MagicMock()

        # Create coordinator
        coordinator = LierdaDataUpdateCoordinator(
            hass=hass,
            client=client,
            update_interval=timedelta(seconds=30),
        )

        # Verify it's an instance of DataUpdateCoordinator
        assert isinstance(coordinator, DataUpdateCoordinator)

    async def test_coordinator_stores_client_reference(self):
        """Test coordinator stores client reference."""
        from custom_components.lierda_iot.coordinator import LierdaDataUpdateCoordinator

        # Create mock instances
        hass = MagicMock()
        client = MagicMock()

        # Create coordinator
        coordinator = LierdaDataUpdateCoordinator(
            hass=hass,
            client=client,
            update_interval=timedelta(seconds=30),
        )

        # Verify client is stored
        assert coordinator.client == client

    async def test_single_device_returns_dict_with_one_entry(self):
        """Test single device returns dict with one entry."""
        from custom_components.lierda_iot.coordinator import LierdaDataUpdateCoordinator

        # Create mock Home Assistant instance
        hass = MagicMock()

        # Create mock client
        client = MagicMock()
        client.auth_data = MagicMock()

        # Create single device
        device = Device(
            id=42,
            name="Single Device",
            type=1,
            mac_id="SINGLE:MAC",
            attributes={"LIVE": "ON"},
            available=True,
            firmware_version="2.0.0",
            ddc_id=10,
        )

        # Mock get_all_devices
        client.get_all_devices = AsyncMock(return_value=[device])

        # Create coordinator
        coordinator = LierdaDataUpdateCoordinator(
            hass=hass,
            client=client,
            update_interval=timedelta(seconds=30),
        )

        # Call _async_update_data
        result = await coordinator._async_update_data()

        # Verify single entry
        assert len(result) == 1
        assert 42 in result
        assert result[42] == device
