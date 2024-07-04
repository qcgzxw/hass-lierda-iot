"""Constants for the Lierda iot integration."""
from homeassistant.const import Platform

BAND = "Lierda iot"
DOMAIN = "lierda_iot"
VERSION = "1.0.0"
ENTRIES_VERSION = 1

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.LIGHT,
    Platform.SWITCH,
    Platform.COVER,
]

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_REFRESH_INTERVAL = "refresh_interval"
CONF_FILTER_DEVICE = "filter_device"
CONF_REMEMBER_ME = "remember_me"

CONF_KEY_USERNAME = "username"
CONF_KEY_PASSWORD = "password"
CONF_KEY_USER_AUTH_DATA = "user_auth_data"
CONF_KEY_DEVICES = "devices"
CONF_KEY_REFRESH_INTERVAL = "refresh_interval"

CONF_RELOAD_FLAG = "flag_reload"

LIERDA_DEVICES = "lierda_devices"

DEFAULT_REFRESH_INTERVAL = 300
