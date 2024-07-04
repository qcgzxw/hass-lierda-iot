import asyncio
import json
import logging
import time

import aiohttp

from .error import LierdaAuthError, LierdaApiError, LierdaRequestInvalid, LierdaRequestTimeout

_LOGGER = logging.getLogger(__name__)

API_URL = "https://www.lierdalux.cn/action"

ACTION_LOGIN = "login"
ACTION_CMD = "cmd"
ACTION_GET_DEVICE_LIST_BY_USER_ID = "getDeviceListByUserId"
ACTION_GET_DEVICE_BY_DEVICE_ID = "getDeviceByDeviceId"
ACTION_GET_DDC_BY_DEVICE_ID = "getDeviceByDeviceId"


class _LierdaRequest:
    @staticmethod
    async def post(
            data: dict
    ) -> dict:
        _LOGGER.debug(data)
        ten_seconds_timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=ten_seconds_timeout) as session:
            try:
                async with session.post(API_URL, json=data) as response:
                    if response.status != 200:
                        raise LierdaRequestInvalid("post failed. status code: %s" % response.status)
                    resp_data = await response.json()
                    _LOGGER.debug(resp_data)
                    return resp_data
            except asyncio.TimeoutError as e:
                raise LierdaRequestTimeout(str(e))


class LierdaAuth(_LierdaRequest):

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self._data = None

    async def login(self) -> None:
        if not self.username or not self.password:
            raise LierdaAuthError("Username or password is empty")
        try:
            resp = await self.post({
                "pn": ACTION_LOGIN,
                "username": self.username,
                "password": self.password
            })

            if resp is None:
                raise LierdaAuthError("API response is empty")
            if not resp['success']:
                raise LierdaAuthError(resp['msg'])
            if resp is not None and resp['data'] is not None:
                data = resp['data']
                self._data = data
        except Exception as e:
            raise LierdaAuthError(str(e))

    @property
    def data(self):
        if self._data is None:
            raise LierdaAuthError("not authorized")
        return {k: v for k, v in self._data.items() if k in ('userid', 'username', 'role', 'parentid', 'nat', 'phone')}


class LierdaApi(_LierdaRequest):

    def __init__(
            self,
            userid: int,
            username: str,
            role: int,
            parentid: int,
            nat: str,
            phone: str,
    ):
        self.userid = userid
        self.username = username
        self.role = role
        self.parentid = parentid
        self.nat = nat
        self.phone = phone

    async def build_common_data(
            self,
            pn: str
    ) -> dict:
        return {
            'pn': pn,
            'userid': self.userid,
            'ibmsuserid': self.userid,
            'ibmsuserole': self.role,
            'ibmsparentid': self.parentid,
            'ibmsnat': self.nat,
        }

    async def action(
            self,
            pn: str,
            data: [dict | None]
    ) -> dict:
        common_data = await self.build_common_data(pn)
        resp = await self.post({**common_data, **data} if data is not None else common_data)
        if resp is None:
            raise LierdaApiError("API response is empty")
        if not resp['success']:
            raise LierdaApiError(resp['message'])
        return resp

    async def get_device_list_by_user_id(self):
        return await self.action(ACTION_GET_DEVICE_LIST_BY_USER_ID, {
            "uid": self.userid,
            "role": self.userid,
        })

    async def get_ddc_list_by_user_id(self):
        return await self.action(ACTION_GET_DDC_BY_DEVICE_ID)


class LierdaDeviceApi(LierdaApi):
    def __init__(
            self,
            userid: int,
            username: str,
            role: int,
            parentid: int,
            nat: str,
            phone: str,
            id: int,
            macid: str,
            ddcmac: str,
    ):
        super().__init__(userid, username, role, parentid, nat, phone)
        self.id = id
        self.macid = macid
        self.ddcmac = ddcmac

    def _cmd_protocol(
            self,
            attributes: dict,
    ):
        return {
            "sourceId": "123456",
            "serialNum": int(time.time()) % 10000,
            "requestType": "cmd",
            "id": self.macid,
            "ddcId": self.ddcmac,
            "attributes": attributes
        }

    async def get_device_by_device_id(self):
        return await self.action(ACTION_GET_DEVICE_BY_DEVICE_ID, {"id": self.id})

    async def cmd(
            self,
            attributes: dict,
    ):
        return await self.action(ACTION_CMD, {"cmdStr": json.dumps(self._cmd_protocol(attributes))})
