# custom_components/lierda_iot/models/device.py
"""Device data model."""
import json
from dataclasses import dataclass
from typing import Any


@dataclass
class Device:
    """Device data for Lierda IoT."""

    id: int
    name: str
    type: int
    mac_id: str
    ddc_mac: str
    ddc_id: int
    ddc_name: str
    attributes: dict[str, Any]
    available: bool
    firmware_version: str | None

    @classmethod
    def from_api_response(cls, data: dict) -> "Device":
        """Create Device from API response.

        Args:
            data: API response dictionary

        Returns:
            Device instance

        Raises:
            ValueError: If required field is missing
        """
        try:
            # Extract required fields
            device_id = data["id"]
            device_type = data["type"]
            mac_id = data["macid"]  # API returns lowercase 'macid'
            attributes_str = data["attributes"]
            ddc_id = data["ddcId"]
            ddc_mac = data["ddcmac"]  # API returns lowercase 'ddcmac'
            ddc_name = data["ddcname"]  # API returns lowercase 'ddcname'

            # Use alias if available and not empty, otherwise use name
            alias = data.get("alias")
            name = alias if alias else data["name"]

        except KeyError as e:
            raise ValueError(f"Missing required field: {e.args[0]}") from e

        # Parse attributes JSON string
        try:
            attributes = json.loads(attributes_str)
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Invalid attributes JSON: {e}") from e

        # Determine availability based on LIVE attribute
        live_status = attributes.get("LIVE")
        available = live_status == "ON"

        # Extract firmware version (optional)
        firmware_version = attributes.get("FWV")

        return cls(
            id=device_id,
            name=name,
            type=device_type,
            mac_id=mac_id,
            ddc_mac=ddc_mac,
            ddc_id=ddc_id,
            ddc_name=ddc_name,
            attributes=attributes,
            available=available,
            firmware_version=firmware_version,
        )

    def get_attribute(self, key: str) -> Any:
        """Get attribute value by key.

        Args:
            key: Attribute key

        Returns:
            Attribute value, or None if key not found
        """
        return self.attributes.get(key)

    @property
    def device_type(self) -> int:
        """Alias for type field for compatibility."""
        return self.type

    @property
    def online(self) -> bool:
        """Alias for available field for compatibility."""
        return self.available

    @property
    def room_name(self) -> str | None:
        """Get room name from DDC name."""
        return self.ddc_name
