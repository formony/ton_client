# -*- coding: utf-8 -*-

import unittest
from binascii import unhexlify
from mnemonic.mnemonic import Mnemonic
import os

from ton_client.client import TonlibClientFutures

proj_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')


class ClientKeyingTestCase(unittest.TestCase):
    keystore = os.path.join(proj_path, 'tmp')
    vect = '000000000000000000000000000000000000000000000000'
    passwd = '1234567890'
    mn = Mnemonic("english")
    mn_phrase = mn.to_mnemonic(unhexlify(vect))

    def _test_create_new_key(self):
        t = TonlibClientFutures(keystore=self.keystore)

        ft = t.create_new_key(local_password=self.passwd, mnemonic=self.mn_phrase)
        res = ft.result()
        self.assertIsInstance(res, dict)
        self.assertEqual(res['@type'], 'key')

        ft = t.delete_key(public_key=res['public_key'])
        res = ft.result()
        self.assertIsInstance(res, dict)
        self.assertEqual(res['@type'], 'ok')

    def test_export_key(self):
        t = TonlibClientFutures(keystore=self.keystore)

        ft1 = t.create_new_key(local_password=self.passwd, mnemonic=self.mn_phrase)
        res1 = ft1.result()
        self.assertIsInstance(res1, dict)
        self.assertEqual(res1['@type'], 'key')

        ft2 = t.export_key(public_key=res1['public_key'], secret=res1['secret'], local_password=self.passwd)
        res2 = ft2.result()
        self.assertIsInstance(res2, dict)
        self.assertEqual(res2['@type'], 'exportedKey')

        ft = t.delete_key(res1['public_key'])
        res3 = ft.result()
        self.assertIsInstance(res3, dict)
        self.assertEqual(res3['@type'], 'ok')
