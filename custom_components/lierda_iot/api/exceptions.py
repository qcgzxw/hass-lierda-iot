# custom_components/lierda_iot/api/exceptions.py
"""Custom exceptions for Lierda API."""


class LierdaError(Exception):
    """Base exception for Lierda integration."""


class LierdaApiError(LierdaError):
    """Base exception for Lierda API errors."""


class LierdaAuthError(LierdaApiError):
    """Exception raised for authentication errors."""


class LierdaConnectionError(LierdaApiError):
    """Exception raised for connection errors."""


class LierdaTimeoutError(LierdaApiError):
    """Exception raised for timeout errors."""
