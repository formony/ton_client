# -*- coding: utf-8 -*-

import os
import unittest

from ton_client.client import TonlibClientFutures

proj_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')


class ClientOnlineTestCase(unittest.TestCase):
    def test_raw_getaccount_state(self):
        t = TonlibClientFutures()
        ft = t.raw_get_account_state('-1:DD74DD3DA6E2AC5A5A090875BD08D3F8E61388BD200AA7BBC70957640D732236')
        res = ft.result()
        self.assertIsInstance(res, dict)
        self.assertEqual('raw.accountState', res['@type'])

    def test_raw_get_transactions(self):
        t = TonlibClientFutures()
        ft = t.raw_get_transactions(
            '-1:DD74DD3DA6E2AC5A5A090875BD08D3F8E61388BD200AA7BBC70957640D732236',
            '429475000001',
            '2AF9BC9B61CE16A99FCA33ED2025AC59C44475626A65AC65A9533384AFE7023B'
        )
        res = ft.result()
        self.assertIsInstance(res, dict)
        self.assertEqual('raw.transactions', res['@type'])
