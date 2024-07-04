import asyncio
import json
import logging
import threading
import time

from .error import LierdaApiError
from .lierda_api import LierdaDeviceApi

_LOGGER = logging.getLogger(__name__)


def load_attributes(attributes: str):
    return json.loads(attributes) if type(attributes) is str else {attributes if type(attributes) is dict else {}}


class LierdaDevice(threading.Thread):

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
                 attribute_keys: dict,
                 auth_data: dict,
                 ):
        threading.Thread.__init__(self)
        self._is_run = False
        self._refresh_interval = 30
        self._updates = []

        self._id = id
        self._name = name
        self._type = type
        self._alias = alias
        self._attributes = load_attributes(attributes)
        self._commonuse = commonuse
        self._ddc_id = ddcId
        self._isnew = isnew
        self._macid = macid
        self._ddcmac = ddcmac
        self._ddcname = ddcname
        self._userid = userid
        self._dicon = dicon
        self._link = link
        self._typ = typ
        self._trigger = trigger
        self._attribute_keys = attribute_keys

        self.device_api = LierdaDeviceApi(
            id=self._id,
            macid=self._macid,
            ddcmac=self._ddcmac,
            **auth_data,
        )

    @property
    def id(self) -> int:
        return self._id

    @property
    def device_id(self) -> int:
        return self._id

    @property
    def device_type(self) -> int:
        return self._type

    @property
    def type(self) -> int:
        return self._type

    @property
    def link(self) -> str:
        return self._link

    @property
    def name(self) -> str:
        return self._attributes['NAM'] if 'NAM' in self._attributes else (self._alias if self._alias else self._name)

    @property
    def ddc_id(self) -> int:
        return self._ddc_id

    @property
    def mac_id(self) -> str:
        return self._macid

    @property
    def available(self) -> bool:
        return self._attributes["LIVE"] == "ON" if "LIVE" in self._attributes else False

    @property
    def last_common_time(self) -> int:
        return int(self._attributes["LAST_COMMON_TIME"] if "LAST_COMMON_TIME" in self._attributes else 0)

    @property
    def firmware_version(self) -> int:
        return self._attributes["FWV"] if "FWV" in self._attributes else None

    @property
    def attributes(self) -> str:
        return self._attributes

    def get_attribute(self, attr: str):
        if hasattr(self, attr):
            return getattr(self, attr)
        return self._attributes.get(attr)

    def set_attribute(self, attr: str, value):
        if self._get_lierda_attribute(attr) is None:
            _LOGGER.error("Attribute %s not found", attr)
            return
        self._attributes[self._get_lierda_attribute(attr)] = value

    def update_attributes(self, new_attributes: dict):
        for key, value in new_attributes:
            if key in self._attribute_keys.values():
                self.set_attribute(key, value)

    def _get_lierda_attribute(self, attr: str) -> str | None:
        return self._attribute_keys.get(attr, None)

    async def remote_set_attribute(self, attr: str, value):
        try:
            await self.device_api.cmd({self._get_lierda_attribute(attr): str(value)})
        except Exception as e:
            raise LierdaApiError(str(e))

    async def remote_update_attributes(self):
        try:
            resp = await self.device_api.get_device_by_device_id()
            for data in resp['data']:
                if data['id'] == self._id:
                    new_attributes = data['attributes']
                    self._attributes = load_attributes(new_attributes)
                    self.update_all()
                    break

        except Exception as e:
            raise LierdaApiError(str(e))

    async def entry_set_attribute(self, attr: str, value):
        await self.remote_set_attribute(attr, value)
        self.set_attribute(attr, value)

    def entry_get_attribute(self, attr: str):
        return self.get_attribute(self._attribute_keys.get(attr, attr))

    def register_update(self, update):
        self._updates.append(update)

    def update_all(self):
        for update in self._updates:
            update()

    def set_refresh_interval(self, interval: int):
        self._refresh_interval = max(interval, 30)

    def open(self):
        if not self._is_run:
            self._is_run = True
            threading.Thread.start(self)

    def close(self):
        if self._is_run:
            self._is_run = False

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while self._is_run:
            try:
                loop.run_until_complete(
                    asyncio.wait_for(self.remote_update_attributes(), timeout=self._refresh_interval))
            except asyncio.TimeoutError:
                _LOGGER.error("Device %s update timed out", self.id)
            except LierdaApiError as e:
                _LOGGER.error(e)
            finally:
                time.sleep(self._refresh_interval)
        loop.close()
