# -*- coding: utf-8 -*-

import unittest

from ton_client.client import TonlibClientFutures, TonlibClientBase
from ton_client.utils import raw_to_userfriendly


class ClientBaseTestCase(unittest.TestCase):
    def test_tonlib_client_base(self):
        t = TonlibClientBase()
        with self.assertRaises(RuntimeError):
            t.testgiver_getaccount_address()

# TODO wait for fixing bugs in ton-blockchain/ton


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
        print(res)
        self.assertIsInstance(res, dict)
        self.assertEqual('testGiver.accountState', res['@type'])

    def test_testgiver_getaccount_state_parallel(self):
        t = TonlibClientFutures(threads=5)
        fts = [t.testgiver_getaccount_state() for _ in range(10)]
        ress = [f.result() for f in fts]
        [self.assertIsInstance(r, dict) for r in ress]
        [self.assertEqual('testGiver.accountState', r['@type']) for r in ress]
