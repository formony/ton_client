# -*- coding: utf-8 -*-

import unittest
import uvloop

from ton_client.client import TonlibClientAsyncio
from ton_client.utils import coro_result


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
