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
        from custom_components.lierda_iot.lierda_devices import LIERDA_DEVICES

        try:
            # Fetch all devices from API
            all_devices = await self.client.get_all_devices()

            device_dict = {}
            for device in all_devices:
                # Skip virtual/placeholder devices
                if device.mac_id == "0000000000000000":
                    _LOGGER.debug("Skipping virtual device %s (%s)", device.name, device.id)
                    continue

                # Check if device type is supported
                if device.type not in LIERDA_DEVICES:
                    # Only log once per fetch, rather than in every platform
                    _LOGGER.debug("Unknown or unsupported device type %s for device %s", device.type, device.id)
                    continue

                device_dict[device.id] = device

            _LOGGER.debug("Updated %d devices", len(device_dict))

            return device_dict

        except LierdaApiError as err:
            # Wrap LierdaApiError in UpdateFailed for HA coordinator
            _LOGGER.error("Failed to update devices: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err
