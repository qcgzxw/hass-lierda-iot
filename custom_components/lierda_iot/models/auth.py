# custom_components/lierda_iot/models/auth.py
"""Authentication data model."""
from dataclasses import dataclass


@dataclass
class AuthData:
    """Authentication data for Lierda API."""

    userid: int
    username: str
    domain: str
    role: int
    parentid: int
    nat: str
    phone: str

    @classmethod
    def from_api_response(cls, data: dict) -> "AuthData":
        """Create AuthData from API response.

        Args:
            data: API response dictionary

        Returns:
            AuthData instance

        Raises:
            ValueError: If required field is missing
        """
        try:
            return cls(
                userid=data["userid"],
                username=data["username"],
                domain=data["domain"],
                role=data["role"],
                parentid=data["parentid"],
                nat=data["nat"],
                phone=data["phone"],
            )
        except KeyError as e:
            raise ValueError(f"Missing required field: {e.args[0]}") from e
