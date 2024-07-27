import asyncio
import unittest

from .core.lierda_api import LierdaAuth, LierdaApi

domain = "www.lierdalux.cn"
USERNAME = "test"
PASSWORD = "test"


class TestLierdaAuth(unittest.TestCase):
    def setUp(self):
        self.auth = LierdaAuth(USERNAME, PASSWORD, domain)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_login(self):
        self.loop.run_until_complete(self.auth.login())
        self.assertIsNotNone(self.auth.data)
        self.assertEqual(self.auth.data['userid'], 2900)


class TestLierdaAPI(unittest.TestCase):

    def setUp(self):
        self.auth = LierdaAuth(USERNAME, PASSWORD, domain)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.auth.login())
        self.api = LierdaApi(**self.auth.data, domain=domain)

    def tearDown(self):
        self.loop.close()

    async def async_test_api(self):
        try:
            response = await self.api.get_device_list_by_user_id()
            self.assertTrue(response['success'])
        except Exception as e:
            self.fail(f"Exception occurred: {e}")

    def test_api(self):
        self.loop.run_until_complete(self.async_test_api())


if __name__ == '__main__':
    unittest.main()
