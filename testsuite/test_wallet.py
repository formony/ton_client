# -*- coding: utf-8 -*-

import unittest
import os

from ton_client.client import TonlibClientFutures

proj_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')


class TestgiverTestCase(unittest.TestCase):
    keystore = os.path.join(proj_path, 'tmp')
    decrypt_password = '1234567890'
    encrypted_public_key = 'Pub3Dt+JCpOPtuOqZHWLmsb7mIHU5JG3MHIcrojzQ/N5TmfL'
    encrypted_secret = 'JlzkJ2sOr9R38e0DzwRBBY1sYwwWWeCd2sUI+RyzH3A='
    t = TonlibClientFutures(keystore=keystore)

    def _test_wallet_init(self):
        res_decrypt_key = self.t.decrypt_key(
            public_key=self.encrypted_public_key,
            secret=self.encrypted_secret,
            local_password=self.decrypt_password
        ).result()
        self.assertIsInstance(res_decrypt_key, dict)
        decrypted_public_key = res_decrypt_key['public_key']
        decrypted_secret = res_decrypt_key['secret']

        res_wallet_init = self.t.wallet_init(
            public_key=decrypted_public_key,
            secret=decrypted_secret
        ).result()
        self.assertIsInstance(res_wallet_init, dict)
        self.assertEqual('ok', res_wallet_init['@type'])

        res_wallet_account_address = self.t.wallet_get_account_address(
            public_key=decrypted_public_key
        ).result()
        self.assertIsInstance(res_wallet_account_address, dict)
        self.assertEqual('accountAddress', res_wallet_account_address['@type'])
        account_address = res_wallet_account_address['account_address']

        res_wallet_account_state = self.t.wallet_get_account_state(
            address=account_address
        ).result()
        self.assertIsInstance(res_wallet_account_state, dict)

        res_delete_decrypted_key = self.t.delete_key(
            public_key=decrypted_public_key,
            secret=decrypted_secret
        ).result()
        self.assertIsInstance(res_delete_decrypted_key, dict)
        self.assertNotEqual('error', res_delete_decrypted_key['@type'])
