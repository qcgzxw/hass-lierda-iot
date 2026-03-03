# tests/test_api/test_client.py
"""Tests for Lierda API client."""

import pytest
from aioresponses import aioresponses

from custom_components.lierda_iot.api.client import LierdaClient
from custom_components.lierda_iot.api.exceptions import (
    LierdaAuthError,
    LierdaConnectionError,
    LierdaTimeoutError,
)
from custom_components.lierda_iot.models.auth import AuthData


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
                "role": 1,
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
            assert auth_data.role == 1
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
                "role": 1,
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
            assert len(m.requests) == 1
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
                "role": 1,
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
