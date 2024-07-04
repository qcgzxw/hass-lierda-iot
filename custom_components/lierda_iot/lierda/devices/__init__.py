from ..core.device import LierdaDevice
from ..devices.curtain import LierdaCurtainDevice
from ..devices.door import LierdaDoorDevice
from ..devices.light import LierdaLightDevice
from ..devices.switch import LierdaSwitchDevice

TYPE_LT_CTM = 1
TYPE_SW_TK2 = 2
TYPE_SW_TK3 = 3
TYPE_SW_TK4 = 4
TYPE_WD_RXJ = 5
TYPE_WD_DYK = 6
TYPE_SS_DOR = 10
TYPE_DL_LCK = 11

TYPE_CL_R1M = 26

TYPE_SW_KY1 = 53
TYPE_SW_KY2 = 54
TYPE_SW_KY3 = 55
TYPE_SW_KY4 = 56
TYPE_SW_KY6 = 58

DOOR_LIST = (
    TYPE_SS_DOR,
)
LIGHT_LIST = (
    TYPE_LT_CTM,
    TYPE_CL_R1M,
)

LOCK_LIST = (
    TYPE_DL_LCK,
)

CURTAIN_LIST = (
    TYPE_WD_RXJ,
    TYPE_WD_DYK,
)

SWITCH_LIST = (
    TYPE_SW_TK2,
    TYPE_SW_TK3,
    TYPE_SW_TK4,
    TYPE_SW_KY1,
    TYPE_SW_KY2,
    TYPE_SW_KY3,
    TYPE_SW_KY4,
    TYPE_SW_KY6,
)


def device_selector(
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
) -> [LierdaDevice | None]:
    try:
        if macid == "0000000000000000":
            # 虚拟设备
            return None
        if type in DOOR_LIST:
            device = LierdaDoorDevice(id, name, type, alias, attributes, commonuse, ddcId, isnew, macid, ddcmac,
                                      ddcname, userid, dicon, link, typ, trigger, auth_data)
        elif type in LIGHT_LIST:
            device = LierdaLightDevice(id, name, type, alias, attributes, commonuse, ddcId, isnew, macid, ddcmac,
                                       ddcname, userid, dicon, link, typ, trigger, auth_data)
        elif type in SWITCH_LIST:
            device = LierdaSwitchDevice(id, name, type, alias, attributes, commonuse, ddcId, isnew, macid, ddcmac,
                                        ddcname, userid, dicon, link, typ, trigger, auth_data)
        elif type in CURTAIN_LIST:
            device = LierdaCurtainDevice(id, name, type, alias, attributes, commonuse, ddcId, isnew, macid, ddcmac,
                                         ddcname, userid, dicon, link, typ, trigger, auth_data)
        else:
            device = None
    except ModuleNotFoundError:
        device = None
    return device
