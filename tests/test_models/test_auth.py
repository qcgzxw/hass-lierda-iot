# tests/test_models/test_auth.py
"""Tests for AuthData model."""
import pytest
from custom_components.lierda_iot.models.auth import AuthData


def test_auth_data_creation():
    """Test AuthData can be created with all fields."""
    auth = AuthData(
        userid=12345,
        username="test@example.com",
        domain="www.lierdalux.cn",
        role=1,
        parentid=0,
        nat="CN",
        phone="13800138000",
    )
    assert auth.userid == 12345
    assert auth.username == "test@example.com"
    assert auth.domain == "www.lierdalux.cn"
    assert auth.role == 1
    assert auth.parentid == 0
    assert auth.nat == "CN"
    assert auth.phone == "13800138000"


def test_auth_data_from_api_response():
    """Test AuthData can be created from API response."""
    api_response = {
        "userid": 12345,
        "username": "test@example.com",
        "domain": "www.lierdalux.cn",
        "role": 1,
        "parentid": 0,
        "nat": "CN",
        "phone": "13800138000",
    }
    auth = AuthData.from_api_response(api_response)
    assert auth.userid == 12345
    assert auth.username == "test@example.com"
    assert auth.domain == "www.lierdalux.cn"
    assert auth.role == 1
    assert auth.parentid == 0
    assert auth.nat == "CN"
    assert auth.phone == "13800138000"


def test_auth_data_from_api_response_with_extra_fields():
    """Test AuthData ignores extra fields from API response."""
    api_response = {
        "userid": 12345,
        "username": "test@example.com",
        "domain": "www.lierdalux.cn",
        "role": 1,
        "parentid": 0,
        "nat": "CN",
        "phone": "13800138000",
        "extra_field": "should be ignored",
    }
    auth = AuthData.from_api_response(api_response)
    assert auth.userid == 12345
    assert not hasattr(auth, "extra_field")


def test_auth_data_equality():
    """Test AuthData equality based on userid."""
    auth1 = AuthData(
        userid=12345,
        username="test@example.com",
        domain="www.lierdalux.cn",
        role=1,
        parentid=0,
        nat="CN",
        phone="13800138000",
    )
    auth2 = AuthData(
        userid=12345,
        username="different@example.com",
        domain="lsd.lierdalux.cn",
        role=2,
        parentid=1,
        nat="US",
        phone="13900139000",
    )
    # Same userid means equal
    assert auth1.userid == auth2.userid


def test_auth_data_from_api_response_missing_required_field():
    """Test AuthData raises ValueError when required field is missing."""
    api_response = {
        "userid": 12345,
        "username": "test@example.com",
        # domain is missing
        "role": 1,
        "parentid": 0,
        "nat": "CN",
        "phone": "13800138000",
    }
    with pytest.raises(ValueError, match="Missing required field: domain"):
        AuthData.from_api_response(api_response)


def test_auth_data_from_api_response_empty_dict():
    """Test AuthData raises ValueError when all fields are missing."""
    api_response = {}
    with pytest.raises(ValueError, match="Missing required field"):
        AuthData.from_api_response(api_response)
