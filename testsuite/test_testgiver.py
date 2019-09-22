# -*- coding: utf-8 -*-

import unittest
from binascii import unhexlify
import os

from mnemonic import Mnemonic

from ton_client.client import TonlibClientFutures
from ton_client.utils import raw_to_userfriendly

proj_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')


class ClientOfflineTestCase(unittest.TestCase):
    testgiver_address = raw_to_userfriendly('-1:FCB91A3A3816D0F7B8C2C76108B8A9BC5A6B7A55BD79F8AB101C52DB29232260', 0x91)

    def test_testgiver_getaccount_address(self):
        t = TonlibClientFutures()
        ft = t.testgiver_getaccount_address()
        res = ft.result()
        self.assertIsInstance(res, dict)
        self.assertEqual('accountAddress', res['@type'])
        self.assertEqual(self.testgiver_address, res['account_address'])


class ClientOnlineTestCase(unittest.TestCase):
    def test_testgiver_getaccount_state(self):
        t = TonlibClientFutures()
        ft = t.testgiver_getaccount_state()
        res = ft.result()
        self.assertIsInstance(res, dict)
        self.assertEqual('testGiver.accountState', res['@type'])

    def test_testgiver_getaccount_state_parallel(self):
        t = TonlibClientFutures(threads=5)
        fts = [t.testgiver_getaccount_state() for _ in range(10)]
        ress = [f.result() for f in fts]
        [self.assertIsInstance(r, dict) for r in ress]
        [self.assertEqual('testGiver.accountState', r['@type']) for r in ress]


class TestgiverTestCase(unittest.TestCase):
    keystore = os.path.join(proj_path, 'tmp')
    vect = '23454927' * 5
    local_password = '1234567890'
    key_password = 'qwert'
    mn = Mnemonic("english")
    mn_phrase = mn.to_mnemonic(unhexlify(vect)).split(' ')
    t = TonlibClientFutures(keystore=keystore)

    def test_testgiver_init(self):
        res1 = self.t.create_new_key(
            local_password=self.local_password,
            mnemonic=self.mn_phrase
        ).result()

        res2 = self.t.decrypt_key(
            public_key=res1['public_key'],
            secret=res1['secret'],
            local_password=self.local_password
        ).result()

        res3 = self.t.test_wallet_init(
            public_key=res2['public_key'],
            secret=res2['secret']
        ).result()

        self.assertIsInstance(res3, dict)
        self.assertEqual('ok', res3['@type'])

        self.t.delete_key(res2['public_key'])
