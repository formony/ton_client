# -*- coding: utf-8 -*-

import unittest
import asyncio
import uvloop

from ton_client.client import TonlibClientFutures, TonlibClientAsyncio, TonlibClientBase


def coro_result(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class ClientBaseTestCase(unittest.TestCase):
    def test_tonlib_client_base(self):
        t = TonlibClientBase()
        self.assertRaises(RuntimeError, t.testgiver_getaccount_address)


class ClientOfflineTestCase(unittest.TestCase):
    def test_testgiver_getaccount_address(self):
        t = TonlibClientFutures()
        ft = t.testgiver_getaccount_address()
        res = ft.result()
        self.assertIsInstance(res, dict)
        self.assertEqual(res['@type'], 'accountAddress')
        self.assertEqual(res['account_address'], 'Ef+BVndbeTJeXWLnQtm5bDC2UVpc0vH2TF2ksZPAPwcODSkb')


class ClientOnlineTestCase(unittest.TestCase):
    def test_testgiver_getaccount_state(self):
        t = TonlibClientFutures()
        ft = t.testgiver_getaccount_state()
        res = ft.result()
        self.assertIsInstance(res, dict)
        self.assertEqual(res['@type'], 'testGiver.accountState')

    def test_testgiver_getaccount_state_parallel(self):
        t = TonlibClientFutures(threads=5)
        fts = [t.testgiver_getaccount_state() for _ in range(10)]
        ress = [f.result() for f in fts]
        [self.assertIsInstance(r, dict) for r in ress]
        [self.assertEqual(r['@type'], 'testGiver.accountState') for r in ress]


class TonlibTestAsyncCase1(unittest.TestCase):
    def setUp(self):
        uvloop.install()

    def test_testgiver_getaccount_address(self):
        t = TonlibClientAsyncio()
        coro = t.testgiver_getaccount_address()
        res = coro_result(coro)
        self.assertIsInstance(res, dict)
        self.assertEqual(res['@type'], 'accountAddress')
        self.assertEqual(res['account_address'], 'Ef+BVndbeTJeXWLnQtm5bDC2UVpc0vH2TF2ksZPAPwcODSkb')

    def test_testgiver_getaccount_state_parallel(self):
        t = TonlibClientAsyncio(threads=5)
        coros = [t.testgiver_getaccount_state() for _ in range(10)]
        ress = [coro_result(coro) for coro in coros]
        [self.assertIsInstance(r, dict) for r in ress]
        [self.assertEqual(r['@type'], 'testGiver.accountState') for r in ress]
