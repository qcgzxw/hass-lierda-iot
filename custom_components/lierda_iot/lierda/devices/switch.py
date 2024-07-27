import logging
from enum import StrEnum

from ..core.device import LierdaDevice

_LOGGER = logging.getLogger(__name__)


class DeviceAttributes(StrEnum):
    switch1_name = "1键开关"
    switch2_name = "2键开关"
    switch3_name = "3键开关"
    switch4_name = "4键开关"
    switch5_name = "5键开关"
    switch6_name = "6键开关"

    switch_1 = "ky1"
    switch_2 = "ky2"
    switch_3 = "ky3"
    switch_4 = "ky4"
    switch_5 = "ky5"
    switch_6 = "ky6"

    switch_1_key = "KY1"
    switch_2_key = "KY2"
    switch_3_key = "KY3"
    switch_4_key = "KY4"
    switch_5_key = "KY5"
    switch_6_key = "KY6"

    switch_key = "SWI"  # 开关状态和 16进制

    # 不接入
    KEY = "KEY"  # 变化按键index
    rl1_key = "RL1"
    rl2_key = "RL2"
    rl3_key = "RL3"
    rl4_key = "RL4"
    light_key = "RLT"  # 只控制开关 数值:1111


class LierdaSwitchDevice(LierdaDevice):

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
                             DeviceAttributes.switch_key: DeviceAttributes.switch_key,
                             DeviceAttributes.switch_1: DeviceAttributes.switch_1_key,
                             DeviceAttributes.switch_2: DeviceAttributes.switch_2_key,
                             DeviceAttributes.switch_3: DeviceAttributes.switch_3_key,
                             DeviceAttributes.switch_4: DeviceAttributes.switch_4_key,
                             DeviceAttributes.switch_5: DeviceAttributes.switch_5_key,
                             DeviceAttributes.switch_6: DeviceAttributes.switch_6_key,
                         },
                         auth_data=auth_data
                         )

    def is_on(self, attr: str) -> bool:
        swi = int(self.get_attribute(DeviceAttributes.switch_key), 16)
        index = int(attr.removeprefix("ky"))
        if 0 < index <= 6:
            light_mask = 1 << (index - 1)
            return (swi & light_mask) != 0
        else:
            return False

    async def entry_set_attribute(self, attr: str, value):
        await super().entry_set_attribute(attr, value)
        index = int(attr.removeprefix("ky"))
        switch = value == "ON"
        swi = int(self.get_attribute(DeviceAttributes.switch_key), 16)
        if 0 < index <= 6:
            light_mask = 1 << (index - 1)

            if switch:
                swi |= light_mask
            else:
                swi &= ~light_mask

            self.set_attribute(DeviceAttributes.switch_key, f"{swi:#04x}")
