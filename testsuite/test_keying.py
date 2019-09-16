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
    local_password = '1234567890'
    key_password = 'qwerty'
    mn = Mnemonic("english")
    mn_phrase = mn.to_mnemonic(unhexlify(vect)).split(' ')
    t = TonlibClientFutures(keystore=keystore)

    def _create_new_key(self):
        ft = self.t.create_new_key(local_password=self.local_password, mnemonic=self.mn_phrase)
        res = ft.result()
        self.assertIsInstance(res, dict)
        self.assertEqual(res['@type'], 'key')
        return res

    def _delete_key(self, public_key):
        ft = self.t.delete_key(public_key)
        res = ft.result()
        self.assertIsInstance(res, dict)
        self.assertEqual(res['@type'], 'ok')

    def test_create_new_key(self):
        ft = self.t.create_new_key(local_password=self.local_password, mnemonic=self.mn_phrase)
        res = ft.result()
        self.assertIsInstance(res, dict)
        self.assertEqual(res['@type'], 'key')

        ft = self.t.delete_key(public_key=res['public_key'])
        res = ft.result()
        self.assertIsInstance(res, dict)
        self.assertEqual(res['@type'], 'ok')

    def test_export_key(self):
        res1 = self._create_new_key()

        ft2 = self.t.export_key(
            public_key=res1['public_key'],
            secret=res1['secret'],
            local_password=self.local_password
        )
        res2 = ft2.result()
        self.assertIsInstance(res2, dict)
        self.assertEqual(res2['@type'], 'exportedKey')

        self._delete_key(res1['public_key'])

    def _test_export_pem_key(self):
        res1 = self._create_new_key()

        ft2 = self.t.export_pem_key(
            public_key=res1['public_key'],
            secret=res1['secret'],
            local_password=self.local_password,
            key_password=self.key_password
        )
        res2 = ft2.result()
        self.assertIsInstance(res2, dict)
        self.assertEqual(res2['@type'], 'exportedKey')

        self._delete_key(res1['public_key'])

    def test_export_encrypted_key(self):
        res1 = self._create_new_key()

        ft2 = self.t.export_encrypted_key(
            public_key=res1['public_key'],
            secret=res1['secret'],
            local_password=self.local_password,
            key_password=self.key_password
        )
        res2 = ft2.result()
        self.assertIsInstance(res2, dict)
        self.assertEqual(res2['@type'], 'exportedEncryptedKey')

        self._delete_key(res1['public_key'])
