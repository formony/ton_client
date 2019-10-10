# -*- coding: utf-8 -*-

import unittest
import os
from binascii import unhexlify
from mnemonic.mnemonic import Mnemonic

from ton_client.client import TonlibClientFutures

proj_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')


class ClientKeyingTestCase(unittest.TestCase):
    keystore = os.path.join(proj_path, 'tmp')
    vect = '23454927' * 5
    local_password = '1234567890'
    key_password = 'qwert'
    mn = Mnemonic("english")
    mn_phrase = mn.to_mnemonic(unhexlify(vect)).split(' ')
    t = TonlibClientFutures(keystore=keystore)

    def _create_new_key(self):
        ft = self.t.create_new_key(local_password=self.local_password, mnemonic=self.mn_phrase)
        res = ft.result()
        self.assertIsInstance(res, dict)
        self.assertEqual('key', res['@type'])
        return res

    def _delete_key(self, public_key, secret):
        ft = self.t.delete_key(public_key=public_key, secret=secret)
        res = ft.result()
        self.assertIsInstance(res, dict)
        self.assertEqual('ok', res['@type'])

    def test_create_new_key(self):
        res_create_new_key = self.t.create_new_key(
            local_password=self.local_password,
            mnemonic=self.mn_phrase
        ).result()
        self.assertIsInstance(res_create_new_key, dict)
        self.assertEqual('key', res_create_new_key['@type'])

        self._delete_key(public_key=res_create_new_key['public_key'], secret=res_create_new_key['secret'])

    def test_export_key(self):
        res_create_new_key = self._create_new_key()

        res_export_key = self.t.export_key(
            public_key=res_create_new_key['public_key'],
            secret=res_create_new_key['secret'],
            local_password=self.local_password
        ).result()
        self.assertIsInstance(res_export_key, dict)
        self.assertEqual('exportedKey', res_export_key['@type'])

        self._delete_key(public_key=res_create_new_key['public_key'], secret=res_create_new_key['secret'])

    def test_export_pem_key(self):
        res_create_new_key = self._create_new_key()

        res_export_pem_key = self.t.export_pem_key(
            public_key=res_create_new_key['public_key'],
            secret=res_create_new_key['secret'],
            local_password=self.local_password,
            key_password=self.key_password
        ).result()
        self.assertIsInstance(res_export_pem_key, dict)
        self.assertEqual('exportedPemKey', res_export_pem_key['@type'])

        self._delete_key(public_key=res_create_new_key['public_key'], secret=res_create_new_key['secret'])

    def test_import_pem_key(self):
        res_create_new_key = self._create_new_key()

        res_export_pem_key = self.t.export_pem_key(
            public_key=res_create_new_key['public_key'],
            secret=res_create_new_key['secret'],
            local_password=self.local_password,
            key_password=self.key_password
        ).result()
        self.assertIsInstance(res_export_pem_key, dict)
        self.assertEqual('exportedPemKey', res_export_pem_key['@type'])

        self._delete_key(public_key=res_create_new_key['public_key'], secret=res_create_new_key['secret'])

        res_import_pem_key = self.t.import_pem_key(
            pem=res_export_pem_key['pem'],
            key_password=self.key_password,
            local_password=self.local_password
        ).result()
        self.assertIsInstance(res_import_pem_key, dict)
        self.assertEqual('key', res_import_pem_key['@type'])

        self._delete_key(public_key=res_import_pem_key['public_key'], secret=res_import_pem_key['secret'])

    def test_export_encrypted_key(self):
        res_create_new_key = self._create_new_key()

        res_export_encrypted_key = self.t.export_encrypted_key(
            public_key=res_create_new_key['public_key'],
            secret=res_create_new_key['secret'],
            local_password=self.local_password,
            key_password=self.key_password
        ).result()
        self.assertIsInstance(res_export_encrypted_key, dict)
        self.assertEqual('exportedEncryptedKey', res_export_encrypted_key['@type'])

        self._delete_key(public_key=res_create_new_key['public_key'], secret=res_create_new_key['secret'])

    def test_import_encrypted_key(self):
        res_create_new_key = self._create_new_key()

        res_export_encrypted_key = self.t.export_encrypted_key(
            public_key=res_create_new_key['public_key'],
            secret=res_create_new_key['secret'],
            local_password=self.local_password,
            key_password=self.key_password
        ).result()
        self.assertIsInstance(res_export_encrypted_key, dict)
        self.assertEqual('exportedEncryptedKey', res_export_encrypted_key['@type'])

        self._delete_key(public_key=res_create_new_key['public_key'], secret=res_create_new_key['secret'])

        res_import_encrypted_key = self.t.import_encrypted_key(
            encrypted_key=res_export_encrypted_key['data'],
            local_password=self.local_password,
            key_password=self.key_password
        ).result()
        self.assertIsInstance(res_import_encrypted_key, dict)
        self.assertEqual('key', res_import_encrypted_key['@type'])

        self._delete_key(public_key=res_import_encrypted_key['public_key'], secret=res_import_encrypted_key['secret'])

    def test_flat_keying(self):
        res_create_new_key = self._create_new_key()

        res_export_encrypted_key = self.t.export_encrypted_key(
            public_key=res_create_new_key['public_key'],
            secret=res_create_new_key['secret'],
            local_password=self.local_password
        ).result()
        self.assertIsInstance(res_export_encrypted_key, dict)
        self.assertEqual('exportedEncryptedKey', res_export_encrypted_key['@type'])

        self._delete_key(public_key=res_create_new_key['public_key'], secret=res_create_new_key['secret'])

        res_import_encrypted_key = self.t.import_encrypted_key(
            encrypted_key=res_export_encrypted_key['data'],
        ).result()
        self.assertIsInstance(res_import_encrypted_key, dict)
        self.assertEqual('key', res_import_encrypted_key['@type'])

        self._delete_key(public_key=res_import_encrypted_key['public_key'], secret=res_import_encrypted_key['secret'])

    def _test_import_key(self):
        res_import_key = self.t.import_key(
            local_password=self.local_password,
            mnemonic_password=self.key_password,
            mnemonic=self.mn_phrase
        ).result()
        self.assertIsInstance(res_import_key, dict)
        self.assertEqual('key', res_import_key['@type'])

        self._delete_key(public_key=res_import_key['public_key'], secret=res_import_key['secret'])
