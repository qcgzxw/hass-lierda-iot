from enum import StrEnum

from ..core.device import LierdaDevice


class DeviceAttributes(StrEnum):
    name = "light"

    power = "power"
    brightness = "brightness"
    # todo 未实现
    color_temperature = "color_temperature"
    # todo 未实现
    rgb_color = "rgb_color"
    # todo 未实现
    effect = "effect"

    CHK = "CHK"

    power_key = "SWI"
    brightness_key = "LEV"
    color_temperature_key = "Unknown"
    effect_key = "Unknown"
    rgb_color_key = "Unknown"


class LierdaLightDevice(LierdaDevice):

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
                             DeviceAttributes.power: DeviceAttributes.power_key,
                             DeviceAttributes.brightness: DeviceAttributes.brightness_key,
                             DeviceAttributes.color_temperature: DeviceAttributes.color_temperature_key,
                             DeviceAttributes.effect: DeviceAttributes.effect_key,
                             DeviceAttributes.rgb_color: DeviceAttributes.rgb_color_key,
                         },
                         auth_data=auth_data
                         )

    @property
    def power(self) -> bool:
        power = self.entry_get_attribute(DeviceAttributes.power)
        return bool(power) if power is not None else None

    @property
    def brightness(self) -> int | None:
        brightness = self.entry_get_attribute(DeviceAttributes.brightness)
        return int(brightness) if brightness is not None else None

    @property
    def color_temperature(self) -> int | None:
        color_temperature = self.entry_get_attribute(DeviceAttributes.color_temperature)
        return int(color_temperature) if color_temperature is not None else None

    @property
    def effect(self) -> str | None:
        return self.entry_get_attribute(DeviceAttributes.effect)

    @property
    def rgb_color(self) -> str | None:
        return self.entry_get_attribute(DeviceAttributes.rgb_color)

    async def turn_on(self):
        await self.entry_set_attribute(DeviceAttributes.power, "ON")

    async def turn_off(self):
        await self.entry_set_attribute(DeviceAttributes.power, "OFF")

    async def set_brightness(self, brightness: int):
        await self.entry_set_attribute(DeviceAttributes.brightness, brightness)
