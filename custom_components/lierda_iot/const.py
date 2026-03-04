"""Constants for the Lierda iot integration."""
from homeassistant.const import Platform

BAND = "Lierda iot"
DOMAIN = "lierda_iot"
VERSION = "1.1.0"
ENTRIES_VERSION = 2
ENTRY_VERSION = 3

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

CONF_KEY_VERSION = "version"
CONF_KEY_USERNAME = "username"
CONF_KEY_PASSWORD = "password"
CONF_KEY_USER_AUTH_DATA = "user_auth_data"
CONF_KEY_DEVICES = "devices"
CONF_KEY_REFRESH_INTERVAL = "refresh_interval"

DEFAULT_REFRESH_INTERVAL = 300

# Device type constants
TYPE_SS_DOR = 10  # Door sensor
TYPE_CL_R1M = 26  # Light
TYPE_SW_KY1 = 53  # 1-gang switch
TYPE_SW_KY2 = 54  # 2-gang switch
TYPE_SW_KY3 = 55  # 3-gang switch
TYPE_SW_KY4 = 56  # 4-gang switch
TYPE_SW_KY6 = 58  # 6-gang switch
TYPE_WD_RXJ = 5   # Curtain
