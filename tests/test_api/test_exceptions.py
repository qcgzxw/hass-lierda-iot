# tests/test_api/test_exceptions.py
"""Tests for Lierda API exceptions."""
import pytest
from custom_components.lierda_iot.api.exceptions import (
    LierdaError,
    LierdaApiError,
    LierdaAuthError,
    LierdaConnectionError,
    LierdaTimeoutError,
)


def test_lierda_error_is_exception():
    """Test LierdaError is an Exception."""
    assert issubclass(LierdaError, Exception)


@pytest.mark.parametrize(
    "exception_class",
    [
        LierdaApiError,
        LierdaAuthError,
        LierdaConnectionError,
        LierdaTimeoutError,
    ],
)
def test_api_errors_inherit_from_lierda_error(exception_class):
    """Test all API errors inherit from LierdaError."""
    assert issubclass(exception_class, LierdaError)
    assert issubclass(exception_class, LierdaApiError)


@pytest.mark.parametrize(
    "exception_class",
    [
        LierdaError,
        LierdaApiError,
        LierdaAuthError,
        LierdaConnectionError,
        LierdaTimeoutError,
    ],
)
def test_exception_can_be_raised_with_message(exception_class):
    """Test all exception types can be raised with a message."""
    message = "Test error message"
    with pytest.raises(exception_class) as exc_info:
        raise exception_class(message)
    assert str(exc_info.value) == message


def test_exception_can_be_chained():
    """Test exception can be chained."""
    original_error = ValueError("Original error")
    try:
        try:
            raise original_error
        except ValueError as err:
            raise LierdaConnectionError("Connection failed") from err
    except LierdaConnectionError as exc:
        assert exc.__cause__ == original_error
