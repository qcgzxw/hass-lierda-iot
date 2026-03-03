# custom_components/lierda_iot/api/client.py
"""Lierda API client."""

import asyncio
import logging
from typing import Any, Optional

import aiohttp

from custom_components.lierda_iot.api.exceptions import (
    LierdaAuthError,
    LierdaConnectionError,
    LierdaTimeoutError,
)
from custom_components.lierda_iot.models.auth import AuthData

_LOGGER = logging.getLogger(__name__)


class LierdaClient:
    """Client for interacting with Lierda IoT API."""

    def __init__(self) -> None:
        """Initialize the Lierda client."""
        self._session: Optional[aiohttp.ClientSession] = None
        self.auth_data: Optional[AuthData] = None

    def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session.

        Returns:
            aiohttp.ClientSession instance
        """
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session is not None and not self._session.closed:
            await self._session.close()

    async def _request(self, domain: str, data: dict[str, Any]) -> dict[str, Any]:
        """Make an async HTTP POST request to the Lierda API.

        Args:
            domain: API domain (e.g., www.lierdalux.cn)
            data: JSON payload to send

        Returns:
            API response as dictionary

        Raises:
            LierdaConnectionError: If connection fails
            LierdaTimeoutError: If request times out
        """
        url = f"https://{domain}/action"
        session = self._get_session()

        try:
            async with session.post(url, json=data) as response:
                if response.status != 200:
                    raise LierdaConnectionError(
                        f"API request failed with status code: {response.status}"
                    )
                result: dict[str, Any] = await response.json()
                return result
        except asyncio.TimeoutError as err:
            _LOGGER.error("Request to %s timed out", url)
            raise LierdaTimeoutError(f"Timeout error: {err}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error to %s: %s", url, err)
            raise LierdaConnectionError(f"Connection error: {err}") from err

    async def login(self, username: str, password: str, domain: str) -> AuthData:
        """Login to Lierda IoT API.

        Args:
            username: User's username
            password: User's password
            domain: API domain (e.g., www.lierdalux.cn)

        Returns:
            AuthData instance with user authentication data

        Raises:
            LierdaAuthError: If credentials are empty or login fails
            LierdaConnectionError: If connection fails
            LierdaTimeoutError: If request times out
        """
        # Validate credentials
        if not username or not password:
            raise LierdaAuthError("Username and password are required")

        # Prepare login request
        request_data = {
            "pn": "login",
            "username": username,
            "password": password,
        }

        _LOGGER.debug("Attempting login for user %s", username)

        try:
            # Make login request
            response = await self._request(domain, request_data)

            # Check if login was successful
            if not response.get("success"):
                error_msg = response.get("msg", "Login failed")
                _LOGGER.error("Login failed for user %s: %s", username, error_msg)
                raise LierdaAuthError(error_msg)

            # Extract data from response
            data = response.get("data")
            if data is None:
                raise LierdaAuthError("Login response missing data field")

            # Add domain to data for AuthData creation
            data["domain"] = domain

            # Create AuthData instance
            self.auth_data = AuthData.from_api_response(data)

            _LOGGER.info("Successfully logged in as user %s", username)

            return self.auth_data

        except (LierdaConnectionError, LierdaTimeoutError):
            # Re-raise connection and timeout errors
            raise
        except Exception as err:
            # Wrap any other unexpected errors
            _LOGGER.error("Unexpected error during login: %s", err)
            raise LierdaAuthError(f"Login failed: {err}") from err
