"""Device type configurations for Lierda IoT."""

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.cover import CoverDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfElectricPotential, Platform, PERCENTAGE

from .const import (
    TYPE_SS_DOR,
    TYPE_LT_CTM,
    TYPE_CL_R1M,
    TYPE_SW_TK2,
    TYPE_SW_TK3,
    TYPE_SW_TK4,
    TYPE_SW_KY1,
    TYPE_SW_KY2,
    TYPE_SW_KY3,
    TYPE_SW_KY4,
    TYPE_SW_KY6,
    TYPE_WD_RXJ,
    TYPE_WD_DYK,
)

LIERDA_DEVICES = {
    TYPE_SS_DOR: {
        "name": "door",
        "entities": {
            "door": {
                "name": "Door",
                "type": Platform.BINARY_SENSOR,
                "device_class": BinarySensorDeviceClass.DOOR,
            },
            "battery_voltage": {
                "name": "Battery Voltage",
                "type": Platform.SENSOR,
                "device_class": SensorDeviceClass.VOLTAGE,
                "unit": UnitOfElectricPotential.VOLT,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            "battery_percentage": {
                "name": "Battery Percentage",
                "type": Platform.SENSOR,
                "device_class": SensorDeviceClass.BATTERY,
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        }
    },
    TYPE_CL_R1M: {
        "name": "light",
        "entities": {
            'light': {
                "type": Platform.LIGHT,
                "icon": "mdi:lightbulb"
            },
        }
    },
    TYPE_LT_CTM: {
        "name": "light",
        "entities": {
            'light': {
                "type": Platform.LIGHT,
                "icon": "mdi:lightbulb"
            },
        }
    },
    TYPE_SW_KY1: {
        "name": "1键开关",
        "entities": {
            "ky1": {
                "name": "开关1",
                "type": Platform.SWITCH
            },
        }
    },
    TYPE_SW_KY2: {
        "name": "2键开关",
        "entities": {
            "ky1": {
                "name": "开关1",
                "type": Platform.SWITCH
            },
            "ky2": {
                "name": "开关2",
                "type": Platform.SWITCH
            },
        }
    },
    TYPE_SW_KY3: {
        "name": "3键开关",
        "entities": {
            "ky1": {
                "name": "开关1",
                "type": Platform.SWITCH
            },
            "ky2": {
                "name": "开关2",
                "type": Platform.SWITCH
            },
            "ky3": {
                "name": "开关3",
                "type": Platform.SWITCH
            },
        }
    },
    TYPE_SW_KY4: {
        "name": "4键开关",
        "entities": {
            "ky1": {
                "name": "开关1",
                "type": Platform.SWITCH
            },
            "ky2": {
                "name": "开关2",
                "type": Platform.SWITCH
            },
            "ky3": {
                "name": "开关3",
                "type": Platform.SWITCH
            },
            "ky4": {
                "name": "开关4",
                "type": Platform.SWITCH
            },
        }
    },
    TYPE_SW_TK2: {
        "name": "2键开关",
        "entities": {
            "ky1": {
                "name": "开关1",
                "type": Platform.SWITCH
            },
            "ky2": {
                "name": "开关2",
                "type": Platform.SWITCH
            },
        }
    },
    TYPE_SW_TK3: {
        "name": "3键开关",
        "entities": {
            "ky1": {
                "name": "开关1",
                "type": Platform.SWITCH
            },
            "ky2": {
                "name": "开关2",
                "type": Platform.SWITCH
            },
            "ky3": {
                "name": "开关3",
                "type": Platform.SWITCH
            },
        }
    },
    TYPE_SW_TK4: {
        "name": "4键开关",
        "entities": {
            "ky1": {
                "name": "开关1",
                "type": Platform.SWITCH
            },
            "ky2": {
                "name": "开关2",
                "type": Platform.SWITCH
            },
            "ky3": {
                "name": "开关3",
                "type": Platform.SWITCH
            },
            "ky4": {
                "name": "开关4",
                "type": Platform.SWITCH
            },
        }
    },
    TYPE_SW_KY6: {
        "name": "6键开关",
        "entities": {
            "ky1": {
                "name": "开关1",
                "type": Platform.SWITCH
            },
            "ky2": {
                "name": "开关2",
                "type": Platform.SWITCH
            },
            "ky3": {
                "name": "开关3",
                "type": Platform.SWITCH
            },
            "ky4": {
                "name": "开关4",
                "type": Platform.SWITCH
            },
            "ky5": {
                "name": "开关5",
                "type": Platform.SWITCH
            },
            "ky6": {
                "name": "开关6",
                "type": Platform.SWITCH
            },
        }
    },
    TYPE_WD_RXJ: {
        "name": "curtain",
        "entities": {
            "curtain": {
                "type": Platform.COVER,
                "device_class": CoverDeviceClass.CURTAIN,
                "icon": "mdi:curtains"
            },
        }
    },
    TYPE_WD_DYK: {
        "name": "curtain",
        "entities": {
            "curtain": {
                "type": Platform.COVER,
                "device_class": CoverDeviceClass.CURTAIN,
                "icon": "mdi:curtains"
            },
        }
    },
}
