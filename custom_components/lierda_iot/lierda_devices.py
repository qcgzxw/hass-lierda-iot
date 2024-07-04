from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.cover import CoverDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfElectricPotential, Platform, PERCENTAGE

from .lierda.devices import *
from .lierda.devices.curtain import DeviceAttributes as CurtainAttributes
from .lierda.devices.door import DeviceAttributes as DoorAttributes
from .lierda.devices.light import DeviceAttributes as LightAttributes
from .lierda.devices.switch import DeviceAttributes as SwitchAttributes

LIERDA_DEVICES = {
    TYPE_SS_DOR: {
        "name": DoorAttributes.name,
        "entities": {
            DoorAttributes.door: {
                "name": "Door",
                "type": Platform.BINARY_SENSOR,
                "device_class": BinarySensorDeviceClass.DOOR,
            },
            DoorAttributes.battery_voltage: {
                "name": "Battery Voltage",
                "type": Platform.SENSOR,
                "device_class": SensorDeviceClass.VOLTAGE,
                "unit": UnitOfElectricPotential.VOLT,
                "state_class": SensorStateClass.MEASUREMENT,
            },
            DoorAttributes.battery_percentage: {
                "name": "Battery Percentage",
                "type": Platform.SENSOR,
                "device_class": SensorDeviceClass.BATTERY,
                "unit": PERCENTAGE,
                "state_class": SensorStateClass.MEASUREMENT,
            },
        }
    },
    TYPE_CL_R1M: {
        "name": LightAttributes.name,
        "entities": {
            'light': {
                "type": Platform.LIGHT,
                "icon": "mdi:lightbulb"
            },
        }
    },
    TYPE_SW_KY1: {
        "name": SwitchAttributes.switch1_name,
        "entities": {
            SwitchAttributes.switch_1: {
                "name": "Switch 1",
                "type": Platform.SWITCH
            },
        }
    },
    TYPE_SW_KY2: {
        "name": SwitchAttributes.switch2_name,
        "entities": {
            SwitchAttributes.switch_1: {
                "name": "Switch 1",
                "type": Platform.SWITCH
            },
            SwitchAttributes.switch_2: {
                "name": "Switch 2",
                "type": Platform.SWITCH
            },
        }
    },
    TYPE_SW_KY3: {
        "name": SwitchAttributes.switch3_name,
        "entities": {
            SwitchAttributes.switch_1: {
                "name": "Switch 1",
                "type": Platform.SWITCH
            },
            SwitchAttributes.switch_2: {
                "name": "Switch 2",
                "type": Platform.SWITCH
            },
            SwitchAttributes.switch_3: {
                "name": "Switch 3",
                "type": Platform.SWITCH
            },
        }
    },
    TYPE_SW_KY4: {
        "name": SwitchAttributes.switch4_name,
        "entities": {
            SwitchAttributes.switch_1: {
                "name": "Switch 1",
                "type": Platform.SWITCH
            },
            SwitchAttributes.switch_2: {
                "name": "Switch 2",
                "type": Platform.SWITCH
            },
            SwitchAttributes.switch_3: {
                "name": "Switch 3",
                "type": Platform.SWITCH
            },
            SwitchAttributes.switch_4: {
                "name": "Switch 4",
                "type": Platform.SWITCH
            },
        }
    },
    TYPE_SW_KY6: {
        "name": SwitchAttributes.switch6_name,
        "entities": {
            SwitchAttributes.switch_1: {
                "name": "Switch 1",
                "type": Platform.SWITCH
            },
            SwitchAttributes.switch_2: {
                "name": "Switch 2",
                "type": Platform.SWITCH
            },
            SwitchAttributes.switch_3: {
                "name": "Switch 3",
                "type": Platform.SWITCH
            },
            SwitchAttributes.switch_4: {
                "name": "Switch 4",
                "type": Platform.SWITCH
            },
            SwitchAttributes.switch_5: {
                "name": "Switch 5",
                "type": Platform.SWITCH
            },
            SwitchAttributes.switch_6: {
                "name": "Switch 6",
                "type": Platform.SWITCH
            },
        }
    },
    TYPE_WD_RXJ: {
        "name": CurtainAttributes.name,
        "entities": {
            CurtainAttributes.name: {
                "type": Platform.COVER,
                "device_class": CoverDeviceClass.CURTAIN,
                "icon": "mdi:curtains"
            },
        }
    },
}
