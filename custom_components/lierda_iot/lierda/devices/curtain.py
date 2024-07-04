from enum import StrEnum

from ..core.device import LierdaDevice


class DeviceAttributes(StrEnum):
    name = "curtain"

    level = "level"
    window = "window"
    mock_is_closing = "mock_is_closing"
    mock_is_opening = "mock_is_opening"

    level_key = "LEV"
    window_key = "WIN"

    CURTAIN_MODE_OPEN = "OPEN"
    CURTAIN_MODE_CLOSE = "CLOSE"
    CURTAIN_MODE_STOP = "STOP"


class LierdaCurtainDevice(LierdaDevice):

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
                             DeviceAttributes.level: DeviceAttributes.level_key,
                             DeviceAttributes.window: DeviceAttributes.window_key,
                         },
                         auth_data=auth_data
                         )

        self._mock_attributes = {
            DeviceAttributes.mock_is_opening: False,
            DeviceAttributes.mock_is_closing: False,
        }

    @property
    def level(self) -> [int | None]:
        return int(self._attributes.get(DeviceAttributes.level_key)) if self._attributes.get(
            DeviceAttributes.level_key) else None

    @property
    def window(self) -> [str | None]:
        # OPEN | CLOSE | STOP
        return self._attributes.get(DeviceAttributes.window_key)

    # todo
    def mock_is_closing(self) -> bool:
        return self._mock_attributes.get(DeviceAttributes.mock_is_closing)

    # todo
    def mock_is_opening(self) -> bool:
        return self._mock_attributes.get(DeviceAttributes.mock_is_opening)
