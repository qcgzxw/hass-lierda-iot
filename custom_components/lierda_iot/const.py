"""Constants for the Lierda iot integration."""
from homeassistant.const import Platform

BAND = "Lierda iot"
DOMAIN = "lierda_iot"
VERSION = "1.1.0"
ENTRIES_VERSION = 2

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
    Platform.LIGHT,
    Platform.SWITCH,
    Platform.COVER,
]
# default
LIERDA_LUX_URL = "www.lierdalux.cn"
LIERDA_LSD_URL = "lsd.lierdalux.cn"
LIERDA_HOTEL_URL = "hotel.lierdalux.cn"
LIERDA_API_LIST = {
    LIERDA_LUX_URL: "智能家具系统",
    LIERDA_LSD_URL: "智能楼宇系统",
    LIERDA_HOTEL_URL: "智能酒店系统",
}

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_LUX_DOMAIN = "lux_domain"
CONF_REFRESH_INTERVAL = "refresh_interval"
CONF_FILTER_DEVICE = "filter_device"
CONF_REMEMBER_ME = "remember_me"

CONF_KEY_VERSION = "version"
CONF_KEY_USERNAME = "username"
CONF_KEY_PASSWORD = "password"
CONF_KEY_USER_AUTH_DATA = "user_auth_data"
CONF_KEY_DEVICES = "devices"
CONF_KEY_REFRESH_INTERVAL = "refresh_interval"

CONF_RELOAD_FLAG = "flag_reload"

LIERDA_DEVICES = "lierda_devices"

DEFAULT_REFRESH_INTERVAL = 300
