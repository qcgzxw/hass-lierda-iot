import logging
from enum import StrEnum

from ..core.device import LierdaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    name = "Door"

    door = "door"
    battery_voltage = "battery_voltage"
    battery_percentage = "battery_percentage"

    door_key = "DOR"
    battery_voltage_key = "BAT"
    battery_percentage_key = "_BAT"


class LierdaDoorDevice(LierdaDevice):

    def __init__(self,
                 id: int,
                 name: str,
                 type: int,
                 alias: str,
                 attributes: str,
                 commonuse: int,
                 ddcId: int,
                 isnew: int,
                 macid: str,
                 ddcmac: str,
                 ddcname: str,
                 userid: int,
                 dicon: str,
                 link: str,
                 typ: str,
                 trigger: int,
                 auth_data: dict,
                 ):
        super().__init__(id=id,
                         name=name,
                         type=type,
                         alias=alias,
                         attributes=attributes,
                         commonuse=commonuse,
                         ddcId=ddcId,
                         isnew=isnew,
                         macid=macid,
                         ddcmac=ddcmac,
                         ddcname=ddcname,
                         userid=userid,
                         dicon=dicon,
                         link=link,
                         typ=typ,
                         trigger=trigger,
                         attribute_keys={
                             DeviceAttributes.door: DeviceAttributes.door_key,
                             DeviceAttributes.battery_voltage: DeviceAttributes.battery_voltage_key,
                             DeviceAttributes.battery_percentage: DeviceAttributes.battery_percentage_key,
                         },
                         auth_data=auth_data
                         )

    @property
    def door(self) -> bool:
        _LOGGER.debug("door is %s", self.entry_get_attribute(DeviceAttributes.door))
        return self.entry_get_attribute(DeviceAttributes.door) == "OPEN"

    @property
    def battery_voltage(self) -> float:
        _LOGGER.debug("battery_voltage is %s", self.entry_get_attribute(DeviceAttributes.battery_voltage))
        return float(self.entry_get_attribute(DeviceAttributes.battery_voltage))

    @property
    def battery_percentage(self):
        _LOGGER.debug("battery_percentage is %s", self.entry_get_attribute(DeviceAttributes.battery_percentage))
        return int(self.entry_get_attribute(DeviceAttributes.battery_percentage).removesuffix("%"))
