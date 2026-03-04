# tests/test_models/test_device.py
"""Tests for Device model."""
import pytest
from custom_components.lierda_iot.models.device import Device


def test_device_creation():
    """Test Device can be created with all fields."""
    device = Device(
        id=12345,
        name="Living Room Light",
        type=53,
        mac_id="AA:BB:CC:DD:EE:FF",
        attributes={"power": "ON", "brightness": 80},
        available=True,
        firmware_version="1.0.5",
        ddc_id=100,
    ddc_mac="00:00:00:00:00:00",
    ddc_name="Test DDC",
    )
    assert device.id == 12345
    assert device.name == "Living Room Light"
    assert device.type == 53
    assert device.mac_id == "AA:BB:CC:DD:EE:FF"
    assert device.attributes == {"power": "ON", "brightness": 80}
    assert device.available is True
    assert device.firmware_version == "1.0.5"
    assert device.ddc_id == 100


def test_device_creation_without_firmware_version():
    """Test Device can be created without firmware version."""
    device = Device(
        id=12345,
        name="Living Room Light",
        type=53,
        mac_id="AA:BB:CC:DD:EE:FF",
        attributes={"power": "ON"},
        available=True,
        firmware_version=None,
        ddc_id=100,
    ddc_mac="00:00:00:00:00:00",
    ddc_name="Test DDC",
    )
    assert device.firmware_version is None


def test_device_from_api_response_with_alias():
    """Test Device can be created from API response with alias."""
    api_response = {
        "id": 12345,
        "alias": "Living Room Light",
        "name": "Default Name",
        "type": 53,
        "macid": "AA:BB:CC:DD:EE:FF",
        "attributes": '{"power": "ON", "LIVE": "ON", "FWV": "1.0.5"}',
        "ddcId": 100,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
    }
    device = Device.from_api_response(api_response)
    assert device.id == 12345
    assert device.name == "Living Room Light"  # Uses alias
    assert device.type == 53
    assert device.mac_id == "AA:BB:CC:DD:EE:FF"
    assert device.attributes == {"power": "ON", "LIVE": "ON", "FWV": "1.0.5"}
    assert device.available is True  # LIVE is ON
    assert device.firmware_version == "1.0.5"  # Extracted from FWV
    assert device.ddc_id == 100


def test_device_from_api_response_without_alias():
    """Test Device uses name when alias is not available."""
    api_response = {
        "id": 12345,
        "name": "Default Name",
        "type": 53,
        "macid": "AA:BB:CC:DD:EE:FF",
        "attributes": '{"power": "ON", "LIVE": "ON"}',
        "ddcId": 100,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
    }
    device = Device.from_api_response(api_response)
    assert device.name == "Default Name"  # Uses name


def test_device_from_api_response_available_when_live_on():
    """Test Device is available when LIVE attribute is ON."""
    api_response = {
        "id": 12345,
        "name": "Test Device",
        "type": 53,
        "macid": "AA:BB:CC:DD:EE:FF",
        "attributes": '{"power": "ON", "LIVE": "ON"}',
        "ddcId": 100,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
    }
    device = Device.from_api_response(api_response)
    assert device.available is True


def test_device_from_api_response_not_available_when_live_off():
    """Test Device is not available when LIVE attribute is OFF."""
    api_response = {
        "id": 12345,
        "name": "Test Device",
        "type": 53,
        "macid": "AA:BB:CC:DD:EE:FF",
        "attributes": '{"power": "ON", "LIVE": "OFF"}',
        "ddcId": 100,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
    }
    device = Device.from_api_response(api_response)
    assert device.available is False


def test_device_from_api_response_not_available_when_live_missing():
    """Test Device is not available when LIVE attribute is missing."""
    api_response = {
        "id": 12345,
        "name": "Test Device",
        "type": 53,
        "macid": "AA:BB:CC:DD:EE:FF",
        "attributes": '{"power": "ON"}',
        "ddcId": 100,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
    }
    device = Device.from_api_response(api_response)
    assert device.available is False


def test_device_from_api_response_without_firmware_version():
    """Test Device firmware_version is None when FWV attribute is missing."""
    api_response = {
        "id": 12345,
        "name": "Test Device",
        "type": 53,
        "macid": "AA:BB:CC:DD:EE:FF",
        "attributes": '{"power": "ON", "LIVE": "ON"}',
        "ddcId": 100,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
    }
    device = Device.from_api_response(api_response)
    assert device.firmware_version is None


def test_device_from_api_response_with_empty_attributes():
    """Test Device can handle empty attributes."""
    api_response = {
        "id": 12345,
        "name": "Test Device",
        "type": 53,
        "macid": "AA:BB:CC:DD:EE:FF",
        "attributes": "{}",
        "ddcId": 100,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
    }
    device = Device.from_api_response(api_response)
    assert device.attributes == {}
    assert device.available is False
    assert device.firmware_version is None


def test_device_get_attribute():
    """Test get_attribute returns value for existing key."""
    device = Device(
        id=12345,
        name="Test Device",
        type=53,
        mac_id="AA:BB:CC:DD:EE:FF",
        attributes={"power": "ON", "brightness": 80},
        available=True,
        firmware_version="1.0.5",
        ddc_id=100,
    ddc_mac="00:00:00:00:00:00",
    ddc_name="Test DDC",
    )
    assert device.get_attribute("power") == "ON"
    assert device.get_attribute("brightness") == 80


def test_device_get_attribute_missing_key():
    """Test get_attribute returns None for missing key."""
    device = Device(
        id=12345,
        name="Test Device",
        type=53,
        mac_id="AA:BB:CC:DD:EE:FF",
        attributes={"power": "ON"},
        available=True,
        firmware_version="1.0.5",
        ddc_id=100,
    ddc_mac="00:00:00:00:00:00",
    ddc_name="Test DDC",
    )
    assert device.get_attribute("missing_key") is None


def test_device_get_attribute_empty_attributes():
    """Test get_attribute returns None when attributes are empty."""
    device = Device(
        id=12345,
        name="Test Device",
        type=53,
        mac_id="AA:BB:CC:DD:EE:FF",
        attributes={},
        available=True,
        firmware_version="1.0.5",
        ddc_id=100,
    ddc_mac="00:00:00:00:00:00",
    ddc_name="Test DDC",
    )
    assert device.get_attribute("any_key") is None


def test_device_from_api_response_with_extra_fields():
    """Test Device ignores extra fields from API response."""
    api_response = {
        "id": 12345,
        "name": "Test Device",
        "type": 53,
        "macid": "AA:BB:CC:DD:EE:FF",
        "attributes": '{"power": "ON", "LIVE": "ON"}',
        "ddcId": 100,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
        "extra_field": "should be ignored",
    }
    device = Device.from_api_response(api_response)
    assert device.id == 12345
    assert not hasattr(device, "extra_field")


def test_device_from_api_response_missing_required_field_id():
    """Test Device raises ValueError when id is missing."""
    api_response = {
        "name": "Test Device",
        "type": 53,
        "macid": "AA:BB:CC:DD:EE:FF",
        "attributes": '{"power": "ON"}',
        "ddcId": 100,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
    }
    with pytest.raises(ValueError, match="Missing required field: id"):
        Device.from_api_response(api_response)


def test_device_from_api_response_missing_required_field_type():
    """Test Device raises ValueError when type is missing."""
    api_response = {
        "id": 12345,
        "name": "Test Device",
        "macid": "AA:BB:CC:DD:EE:FF",
        "attributes": '{"power": "ON"}',
        "ddcId": 100,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
    }
    with pytest.raises(ValueError, match="Missing required field: type"):
        Device.from_api_response(api_response)


def test_device_from_api_response_missing_required_field_macid():
    """Test Device raises ValueError when macId is missing."""
    api_response = {
        "id": 12345,
        "name": "Test Device",
        "type": 53,
        "attributes": '{"power": "ON"}',
        "ddcId": 100,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
    }
    with pytest.raises(ValueError, match="Missing required field: macid"):
        Device.from_api_response(api_response)


def test_device_from_api_response_missing_required_field_attributes():
    """Test Device raises ValueError when attributes is missing."""
    api_response = {
        "id": 12345,
        "name": "Test Device",
        "type": 53,
        "macid": "AA:BB:CC:DD:EE:FF",
        "ddcId": 100,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
    }
    with pytest.raises(ValueError, match="Missing required field: attributes"):
        Device.from_api_response(api_response)


def test_device_from_api_response_missing_required_field_ddcid():
    """Test Device raises ValueError when ddcId is missing."""
    api_response = {
        "id": 12345,
        "name": "Test Device",
        "type": 53,
        "macid": "AA:BB:CC:DD:EE:FF",
        "attributes": '{"power": "ON"}',
    }
    with pytest.raises(ValueError, match="Missing required field: ddcId"):
        Device.from_api_response(api_response)


def test_device_from_api_response_missing_name_and_alias():
    """Test Device raises ValueError when both name and alias are missing."""
    api_response = {
        "id": 12345,
        "type": 53,
        "macid": "AA:BB:CC:DD:EE:FF",
        "attributes": '{"power": "ON"}',
        "ddcId": 100,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
    }
    with pytest.raises(ValueError, match="Missing required field"):
        Device.from_api_response(api_response)


def test_device_from_api_response_empty_dict():
    """Test Device raises ValueError when all fields are missing."""
    api_response = {}
    with pytest.raises(ValueError, match="Missing required field"):
        Device.from_api_response(api_response)


def test_device_from_api_response_with_null_alias():
    """Test Device uses name when alias is null."""
    api_response = {
        "id": 12345,
        "alias": None,
        "name": "Default Name",
        "type": 53,
        "macid": "AA:BB:CC:DD:EE:FF",
        "attributes": '{"power": "ON", "LIVE": "ON"}',
        "ddcId": 100,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
    }
    device = Device.from_api_response(api_response)
    assert device.name == "Default Name"


def test_device_from_api_response_with_empty_alias():
    """Test Device uses name when alias is empty string."""
    api_response = {
        "id": 12345,
        "alias": "",
        "name": "Default Name",
        "type": 53,
        "macid": "AA:BB:CC:DD:EE:FF",
        "attributes": '{"power": "ON", "LIVE": "ON"}',
        "ddcId": 100,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
    }
    device = Device.from_api_response(api_response)
    assert device.name == "Default Name"
