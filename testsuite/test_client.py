# -*- coding: utf-8 -*-

import unittest

from ton_client.client import TonlibClientBase


class ClientBaseTestCase(unittest.TestCase):
    def test_tonlib_client_base(self):
        t = TonlibClientBase()
        with self.assertRaises(RuntimeError):
            t.testgiver_getaccount_address()
