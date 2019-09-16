# -*- coding: utf-8 -*-

import unittest

from ton_client.client import TonlibClientFutures, TonlibClientBase


class ClientBaseTestCase(unittest.TestCase):
    def test_tonlib_client_base(self):
        t = TonlibClientBase()
        with self.assertRaises(RuntimeError):
            t.testgiver_getaccount_address()


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
