# -*- coding: utf-8 -*-

import unittest
from binascii import unhexlify
from mnemonic.mnemonic import Mnemonic
import os
import uvloop

from ton_client.client import TonlibClientAsyncio
from ton_client.utils import coro_result, raw_to_userfriendly

proj_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')


class TonlibTestAsyncCase1(unittest.TestCase):
    testgiver_address = raw_to_userfriendly('-1:FCB91A3A3816D0F7B8C2C76108B8A9BC5A6B7A55BD79F8AB101C52DB29232260', 0x91)

    def setUp(self):
        uvloop.install()

    def test_testgiver_getaccount_address(self):
        t = TonlibClientAsyncio()
        coro = t.testgiver_getaccount_address()
        res = coro_result(coro)
        self.assertIsInstance(res, dict)
        self.assertEqual('accountAddress', res['@type'])
        self.assertEqual(self.testgiver_address, res['account_address'])

    def test_testgiver_getaccount_state_parallel(self):
        t = TonlibClientAsyncio(threads=5)
        coros = [t.testgiver_getaccount_state() for _ in range(10)]
        ress = [coro_result(coro) for coro in coros]
        [self.assertIsInstance(r, dict) for r in ress]
        [self.assertEqual(r['@type'], 'testGiver.accountState') for r in ress]


class TonlibTestAsyncCase2(unittest.TestCase):
    keystore = os.path.join(proj_path, 'tmp')
    vect = '23454927' * 5
    local_password = '1234567890'
    key_password = 'qwert'
    mn = Mnemonic("english")
    mn_phrase = mn.to_mnemonic(unhexlify(vect)).split(' ')
    t = TonlibClientAsyncio(keystore=keystore)

    def _create_new_key(self):
        coro = self.t.create_new_key(local_password=self.local_password, mnemonic=self.mn_phrase)
        res = coro_result(coro)
        self.assertIsInstance(res, dict)
        self.assertEqual(res['@type'], 'key')
        return res

    def _delete_key(self, public_key):
        coro = self.t.delete_key(public_key)
        res = coro_result(coro)
        self.assertIsInstance(res, dict)
        self.assertEqual(res['@type'], 'ok')

    def setUp(self):
        uvloop.install()

    def test_export_key(self):
        res1 = self._create_new_key()

        coro2 = self.t.export_key(
            public_key=res1['public_key'],
            secret=res1['secret'],
            local_password=self.local_password
        )
        res2 = coro_result(coro2)
        self.assertIsInstance(res2, dict)
        self.assertEqual(res2['@type'], 'exportedKey')

        self._delete_key(res1['public_key'])
