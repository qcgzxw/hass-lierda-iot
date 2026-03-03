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
    attributes: dict[str, Any]
    available: bool
    firmware_version: str | None
    ddc_id: int

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
            mac_id = data["macId"]
            attributes_str = data["attributes"]
            ddc_id = data["ddcId"]

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
            attributes=attributes,
            available=available,
            firmware_version=firmware_version,
            ddc_id=ddc_id,
        )

    def get_attribute(self, key: str) -> Any:
        """Get attribute value by key.

        Args:
            key: Attribute key

        Returns:
            Attribute value, or None if key not found
        """
        return self.attributes.get(key)
