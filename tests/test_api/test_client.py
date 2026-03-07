# tests/test_api/test_client.py
"""Tests for Lierda API client."""

import json

import pytest
from aioresponses import aioresponses

from custom_components.lierda_iot.api.client import LierdaClient
from custom_components.lierda_iot.api.exceptions import (
    LierdaApiError,
    LierdaAuthError,
    LierdaConnectionError,
    LierdaTimeoutError,
)
from custom_components.lierda_iot.models.auth import AuthData
from custom_components.lierda_iot.models.device import Device


@pytest.mark.asyncio
class TestLierdaClientLogin:
    """Tests for LierdaClient login functionality."""

    async def test_successful_login_returns_auth_data(self):
        """Test successful login returns AuthData instance."""
        domain = "www.lierdalux.cn"
        username = "testuser"
        password = "testpass"

        # Mock API response
        mock_response = {
            "success": True,
            "msg": "Login successful",
            "data": {
                "userid": 12345,
                "username": username,
                "domain": domain,
                "role": 12345,
                "parentid": 0,
                "nat": "CN",
                "phone": "13800138000",
            },
        }

        client = LierdaClient()

        with aioresponses() as m:
            m.post(
                f"https://{domain}/action",
                payload=mock_response,
                status=200,
            )

            auth_data = await client.login(username, password, domain)

            # Verify returned AuthData
            assert isinstance(auth_data, AuthData)
            assert auth_data.userid == 12345
            assert auth_data.username == username
            assert auth_data.domain == domain
            assert auth_data.role == 12345
            assert auth_data.parentid == 0
            assert auth_data.nat == "CN"
            assert auth_data.phone == "13800138000"

            # Verify auth_data is stored in client
            assert client.auth_data == auth_data

        await client.close()

    async def test_failed_login_with_invalid_credentials_raises_auth_error(self):
        """Test failed login with invalid credentials raises LierdaAuthError."""
        domain = "www.lierdalux.cn"
        username = "wronguser"
        password = "wrongpass"

        mock_response = {
            "success": False,
            "msg": "Invalid username or password",
            "data": None,
        }

        client = LierdaClient()

        with aioresponses() as m:
            m.post(
                f"https://{domain}/action",
                payload=mock_response,
                status=200,
            )

            with pytest.raises(LierdaAuthError) as exc_info:
                await client.login(username, password, domain)

            assert "Invalid username or password" in str(exc_info.value)

        await client.close()

    async def test_empty_username_raises_auth_error(self):
        """Test empty username raises LierdaAuthError."""
        client = LierdaClient()

        with pytest.raises(LierdaAuthError) as exc_info:
            await client.login("", "password", "www.lierdalux.cn")

        assert "Username and password are required" in str(exc_info.value)

        await client.close()

    async def test_empty_password_raises_auth_error(self):
        """Test empty password raises LierdaAuthError."""
        client = LierdaClient()

        with pytest.raises(LierdaAuthError) as exc_info:
            await client.login("username", "", "www.lierdalux.cn")

        assert "Username and password are required" in str(exc_info.value)

        await client.close()

    async def test_empty_username_and_password_raises_auth_error(self):
        """Test empty username and password raises LierdaAuthError."""
        client = LierdaClient()

        with pytest.raises(LierdaAuthError) as exc_info:
            await client.login("", "", "www.lierdalux.cn")

        assert "Username and password are required" in str(exc_info.value)

        await client.close()

    async def test_connection_error_raises_connection_exception(self):
        """Test connection error raises LierdaConnectionError."""
        import aiohttp

        domain = "www.lierdalux.cn"
        username = "testuser"
        password = "testpass"

        client = LierdaClient()

        with aioresponses() as m:
            m.post(
                f"https://{domain}/action",
                exception=aiohttp.ClientError("Network unreachable"),
            )

            with pytest.raises(LierdaConnectionError) as exc_info:
                await client.login(username, password, domain)

            assert "Connection error" in str(exc_info.value)

        await client.close()

    async def test_timeout_error_raises_timeout_exception(self):
        """Test timeout error raises LierdaTimeoutError."""
        domain = "www.lierdalux.cn"
        username = "testuser"
        password = "testpass"

        client = LierdaClient()

        with aioresponses() as m:
            m.post(
                f"https://{domain}/action",
                exception=TimeoutError("Request timed out"),
            )

            with pytest.raises(LierdaTimeoutError) as exc_info:
                await client.login(username, password, domain)

            assert "Timeout error" in str(exc_info.value)

        await client.close()

    async def test_client_timeout_raises_timeout_exception(self):
        """Test asyncio.TimeoutError raises LierdaTimeoutError."""
        import asyncio

        domain = "www.lierdalux.cn"
        username = "testuser"
        password = "testpass"

        client = LierdaClient()

        with aioresponses() as m:
            m.post(
                f"https://{domain}/action",
                exception=asyncio.TimeoutError(),
            )

            with pytest.raises(LierdaTimeoutError) as exc_info:
                await client.login(username, password, domain)

            assert "Timeout error" in str(exc_info.value)

        await client.close()

    async def test_request_sends_correct_payload(self):
        """Test login request sends correct JSON payload."""
        from yarl import URL

        domain = "www.lierdalux.cn"
        username = "testuser"
        password = "testpass"

        mock_response = {
            "success": True,
            "msg": "Login successful",
            "data": {
                "userid": 12345,
                "username": username,
                "domain": domain,
                "role": 12345,
                "parentid": 0,
                "nat": "CN",
                "phone": "13800138000",
            },
        }

        client = LierdaClient()

        with aioresponses() as m:
            m.post(
                f"https://{domain}/action",
                payload=mock_response,
                status=200,
            )

            await client.login(username, password, domain)

            # Verify request was made with correct payload
            # removed
            request_key = ("POST", URL(f"https://{domain}/action"))
            assert request_key in m.requests

            # Get the request call
            requests_list = m.requests[request_key]
            assert len(requests_list) == 1
            request_call = requests_list[0]

            # Verify request body
            expected_payload = {
                "pn": "login",
                "username": username,
                "password": password,
            }
            assert request_call.kwargs["json"] == expected_payload

        await client.close()

    async def test_multiple_logins_update_auth_data(self):
        """Test multiple login calls update stored auth_data."""
        domain = "www.lierdalux.cn"

        # First login response
        mock_response1 = {
            "success": True,
            "msg": "Login successful",
            "data": {
                "userid": 12345,
                "username": "user1",
                "domain": domain,
                "role": 12345,
                "parentid": 0,
                "nat": "CN",
                "phone": "13800138000",
            },
        }

        # Second login response
        mock_response2 = {
            "success": True,
            "msg": "Login successful",
            "data": {
                "userid": 67890,
                "username": "user2",
                "domain": domain,
                "role": 2,
                "parentid": 1,
                "nat": "US",
                "phone": "13900139000",
            },
        }

        client = LierdaClient()

        with aioresponses() as m:
            # First login
            m.post(
                f"https://{domain}/action",
                payload=mock_response1,
                status=200,
            )
            auth_data1 = await client.login("user1", "pass1", domain)
            assert auth_data1.userid == 12345
            assert client.auth_data.userid == 12345

            # Second login
            m.post(
                f"https://{domain}/action",
                payload=mock_response2,
                status=200,
            )
            auth_data2 = await client.login("user2", "pass2", domain)
            assert auth_data2.userid == 67890
            assert client.auth_data.userid == 67890

        await client.close()


@pytest.mark.asyncio
class TestLierdaClientSession:
    """Tests for LierdaClient session management."""

    async def test_session_is_created_on_demand(self):
        """Test aiohttp session is created on demand."""
        client = LierdaClient()
        assert client._session is None

        session = client._get_session()
        assert session is not None

        await client.close()

    async def test_close_closes_session(self):
        """Test close() closes the aiohttp session."""
        client = LierdaClient()

        # Create session
        session = client._get_session()
        assert session is not None
        assert not session.closed

        # Close client
        await client.close()
        assert session.closed

    async def test_close_without_session(self):
        """Test close() works when session was never created."""
        client = LierdaClient()
        # Should not raise any errors
        await client.close()


@pytest.mark.asyncio
class TestLierdaClientDeviceManagement:
    """Tests for LierdaClient device management functionality."""

    async def test_get_all_devices_success(self):
        """Test get_all_devices returns list of Device objects."""
        domain = "www.lierdalux.cn"

        # Setup authenticated client
        client = LierdaClient()
        client.auth_data = AuthData(
            userid=12345,
            username="testuser",
            domain=domain,
            role=1,
            parentid=0,
            nat="CN",
            phone="13800138000",
        )

        # Mock device list response
        mock_response = {
            "success": True,
            "msg": "Success",
            "data": [
                {
                    "id": 1,
                    "name": "Living Room Light",
                    "alias": "Main Light",
                    "type": 53,
                    "macid": "AA:BB:CC:DD:EE:FF",
                    "attributes": '{"LIVE":"ON","FWV":"1.0.0","POWER":"ON"}',
                    "ddcId": 100,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
                },
                {
                    "id": 2,
                    "name": "Bedroom Light",
                    "alias": "",
                    "type": 53,
                    "macid": "11:22:33:44:55:66",
                    "attributes": '{"LIVE":"OFF","FWV":"1.0.1","POWER":"OFF"}',
                    "ddcId": 101,
        "ddcmac": "00:00:00:00:00:00",
        "ddcname": "Test DDC",
                },
            ],
        }

        with aioresponses() as m:
            m.post(
                f"https://{domain}/action",
                payload=mock_response,
                status=200,
            )

            devices = await client.get_all_devices()

            # Verify returned devices
            assert len(devices) == 2
            assert all(isinstance(d, Device) for d in devices)

            # Verify first device
            assert devices[0].id == 1
            assert devices[0].name == "Main Light"
            assert devices[0].type == 53
            assert devices[0].mac_id == "AA:BB:CC:DD:EE:FF"
            assert devices[0].available is True
            assert devices[0].firmware_version == "1.0.0"
            assert devices[0].ddc_id == 100

            # Verify second device
            assert devices[1].id == 2
            assert devices[1].name == "Bedroom Light"
            assert devices[1].available is False

        await client.close()

    async def test_get_all_devices_empty_list(self):
        """Test get_all_devices returns empty list when no devices."""
        domain = "www.lierdalux.cn"

        client = LierdaClient()
        client.auth_data = AuthData(
            userid=12345,
            username="testuser",
            domain=domain,
            role=1,
            parentid=0,
            nat="CN",
            phone="13800138000",
        )

        mock_response = {
            "success": True,
            "msg": "Success",
            "data": [],
        }

        with aioresponses() as m:
            m.post(
                f"https://{domain}/action",
                payload=mock_response,
                status=200,
            )

            devices = await client.get_all_devices()

            assert devices == []
            assert len(devices) == 0

        await client.close()

    async def test_get_all_devices_not_authenticated_raises_error(self):
        """Test get_all_devices raises LierdaApiError when not authenticated."""
        client = LierdaClient()
        # No auth_data set

        with pytest.raises(LierdaApiError) as exc_info:
            await client.get_all_devices()

        assert "Not authenticated" in str(exc_info.value)

        await client.close()

    async def test_get_all_devices_api_failure_raises_error(self):
        """Test get_all_devices raises LierdaApiError on API failure."""
        domain = "www.lierdalux.cn"

        client = LierdaClient()
        client.auth_data = AuthData(
            userid=12345,
            username="testuser",
            domain=domain,
            role=1,
            parentid=0,
            nat="CN",
            phone="13800138000",
        )

        mock_response = {
            "success": False,
            "msg": "Failed to retrieve devices",
            "data": None,
        }

        with aioresponses() as m:
            m.post(
                f"https://{domain}/action",
                payload=mock_response,
                status=200,
            )

            with pytest.raises(LierdaApiError) as exc_info:
                await client.get_all_devices()

            assert "Failed to retrieve devices" in str(exc_info.value)

        await client.close()

    async def test_set_device_attribute_success(self):
        """Test set_device_attribute successfully controls device."""
        domain = "www.lierdalux.cn"

        client = LierdaClient()
        client.auth_data = AuthData(
            userid=12345,
            username="testuser",
            domain=domain,
            role=1,
            parentid=0,
            nat="CN",
            phone="13800138000",
        )

        mock_response = {
            "success": True,
            "msg": "Command sent successfully",
            "data": None,
        }

        with aioresponses() as m:
            m.post(
                f"https://{domain}/action",
                payload=mock_response,
                status=200,
            )

            # Should not raise any errors
            await client.set_device_attribute(
                device_id=1,
                mac_id="AA:BB:CC:DD:EE:FF",
                ddc_mac="DDC123",
                attribute="POWER",
                value="ON",
            )

        await client.close()

    async def test_set_device_attribute_failure_raises_error(self):
        """Test set_device_attribute raises LierdaApiError on failure."""
        domain = "www.lierdalux.cn"

        client = LierdaClient()
        client.auth_data = AuthData(
            userid=12345,
            username="testuser",
            domain=domain,
            role=1,
            parentid=0,
            nat="CN",
            phone="13800138000",
        )

        mock_response = {
            "success": False,
            "msg": "Failed to send command",
            "data": None,
        }

        with aioresponses() as m:
            m.post(
                f"https://{domain}/action",
                payload=mock_response,
                status=200,
            )

            with pytest.raises(LierdaApiError) as exc_info:
                await client.set_device_attribute(
                    device_id=1,
                    mac_id="AA:BB:CC:DD:EE:FF",
                    ddc_mac="DDC123",
                    attribute="POWER",
                    value="ON",
                )

            assert "Failed to send command" in str(exc_info.value)

        await client.close()

    async def test_set_device_attribute_not_authenticated_raises_error(self):
        """Test set_device_attribute raises LierdaApiError when not authenticated."""
        client = LierdaClient()
        # No auth_data set

        with pytest.raises(LierdaApiError) as exc_info:
            await client.set_device_attribute(
                device_id=1,
                mac_id="AA:BB:CC:DD:EE:FF",
                ddc_mac="DDC123",
                attribute="POWER",
                value="ON",
            )

        assert "Not authenticated" in str(exc_info.value)

        await client.close()

    async def test_get_all_devices_sends_correct_payload(self):
        """Test get_all_devices sends correct request payload."""
        from yarl import URL

        domain = "www.lierdalux.cn"

        client = LierdaClient()
        client.auth_data = AuthData(
            userid=12345,
            username="testuser",
            domain=domain,
            role=1,
            parentid=0,
            nat="CN",
            phone="13800138000",
        )

        mock_response = {
            "success": True,
            "msg": "Success",
            "data": [],
        }

        with aioresponses() as m:
            m.post(
                f"https://{domain}/action",
                payload=mock_response,
                status=200,
            )

            # Pre-create session so aioresponses can intercept it
            client._get_session()
            await client.get_all_devices()

            # Verify request payload
            # removed
            request_key = ("POST", URL(f"https://{domain}/action"))
            assert request_key in m.requests

            requests_list = m.requests[request_key]
            assert len(requests_list) == 1
            request_call = requests_list[0]

            expected_payload = {
                "pn": "getDeviceListByUserId",
                "userid": 12345,
                "uid": 12345,
                "role": 1,
                "ibmsuserid": 12345,
                "ibmsuserole": 1,
                "ibmsparentid": 0,
                "ibmsnat": "CN",
            }
            assert request_call.kwargs["json"] == expected_payload

        await client.close()

    async def test_set_device_attribute_sends_correct_cmdstr_payload(self):
        """Test set_device_attribute sends correctly formatted cmdStr."""
        from yarl import URL

        domain = "www.lierdalux.cn"

        client = LierdaClient()
        client.auth_data = AuthData(
            userid=12345,
            username="testuser",
            domain=domain,
            role=1,
            parentid=0,
            nat="CN",
            phone="13800138000",
        )

        def verify_request(url, **kwargs):
            """Callback to verify the request structure."""
            # Verify request structure
            data = kwargs.get("json", {})
            assert data["pn"] == "cmd"
            assert "cmdStr" in data

            # Parse and verify cmdStr JSON
            cmd_str = json.loads(data["cmdStr"])
            assert cmd_str["sourceId"] == 12345  # userid
            assert cmd_str["serialNum"] == "MAC789"  # mac_id
            assert cmd_str["requestType"] == "control"
            assert str(cmd_str["id"]) == "DDC456"  # device_id (int)
            # attribute is removed  # ddc_mac
            assert cmd_str["attributes"] == {"KY1": "ON"}  # list of dicts

        mock_response = {
            "success": True,
            "msg": "Command sent successfully",
            "data": None,
        }

        with aioresponses() as m:
            m.post(
                f"https://{domain}/action",
                payload=mock_response,
                status=200,
                            )

            await client.set_device_attribute(
                device_id=999,
                mac_id="MAC789",
                ddc_mac="DDC456",
                attribute="KY1",
                value="ON",
            )
            
            # Verify request
            request_key = ("POST", URL(f"https://{domain}/action"))
            request_call = m.requests[request_key][0]
            data = request_call.kwargs["json"]
            assert data["pn"] == "cmd"
            cmd_str = json.loads(data["cmdStr"])
            assert cmd_str["sourceId"] == "12345"
            assert isinstance(cmd_str["serialNum"], int)
            assert cmd_str["id"] == "MAC789"
            assert cmd_str["ddcId"] == "DDC456"
            assert cmd_str["attributes"] == {"KY1": "ON"}

        await client.close()
