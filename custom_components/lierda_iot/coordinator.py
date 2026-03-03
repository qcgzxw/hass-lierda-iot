# custom_components/lierda_iot/coordinator.py
"""DataUpdateCoordinator for Lierda IoT integration."""

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.lierda_iot.api.client import LierdaClient
from custom_components.lierda_iot.api.exceptions import LierdaApiError
from custom_components.lierda_iot.models.device import Device

_LOGGER = logging.getLogger(__name__)


class LierdaDataUpdateCoordinator(DataUpdateCoordinator[dict[int, Device]]):
    """Coordinator to manage data updates from Lierda IoT API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: LierdaClient,
        update_interval: timedelta,
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant instance
            client: Lierda API client instance
            update_interval: How often to update data
        """
        super().__init__(
            hass,
            _LOGGER,
            name="Lierda IoT",
            update_interval=update_interval,
        )
        self.client = client

    async def _async_update_data(self) -> dict[int, Device]:
        """Fetch all devices from API.

        Returns:
            Dictionary of devices keyed by device ID

        Raises:
            UpdateFailed: If API request fails
        """
        try:
            # Fetch all devices from API
            devices = await self.client.get_all_devices()

            # Convert list to dict keyed by device ID
            device_dict = {device.id: device for device in devices}

            _LOGGER.debug("Updated %d devices", len(device_dict))

            return device_dict

        except LierdaApiError as err:
            # Wrap LierdaApiError in UpdateFailed for HA coordinator
            _LOGGER.error("Failed to update devices: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err
