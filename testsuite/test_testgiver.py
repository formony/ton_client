# -*- coding: utf-8 -*-

import unittest
from binascii import unhexlify
import os

from mnemonic import Mnemonic

from ton_client.client import TonlibClientFutures
from ton_client.utils import raw_to_userfriendly  # noqa: F401

proj_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')


class ClientOfflineTestCase(unittest.TestCase):
    testgiver_address = raw_to_userfriendly('-1:FCB91A3A3816D0F7B8C2C76108B8A9BC5A6B7A55BD79F8AB101C52DB29232260', 0x91)
    # testgiver_address = 'kf_8uRo6OBbQ97jCx2EIuKm8Wmt6Vb15-KsQHFLbKSMiYIny'

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
        self.assertIsInstance(res, dict)
        self.assertEqual('testGiver.accountState', res['@type'])

    def test_testgiver_getaccount_state_parallel(self):
        t = TonlibClientFutures(threads=5)
        fts = [t.testgiver_getaccount_state() for _ in range(10)]
        ress = [f.result() for f in fts]
        [self.assertIsInstance(r, dict) for r in ress]
        [self.assertEqual('testGiver.accountState', r['@type']) for r in ress]


class TestgiverTestCase(unittest.TestCase):
    keystore = os.path.join(proj_path, 'tmp')
    vect = '23454927' * 5
    local_password = '1234567890'
    key_password = 'qwert'
    mn = Mnemonic("english")
    mn_phrase = mn.to_mnemonic(unhexlify(vect)).split(' ')
    t = TonlibClientFutures(keystore=keystore)

    def test_testgiver_init(self):
        res_create_new_key = self.t.create_new_key(
            local_password=self.local_password,
            mnemonic=self.mn_phrase
        ).result()

        res_decrypt_key = self.t.decrypt_key(
            public_key=res_create_new_key['public_key'],
            secret=res_create_new_key['secret'],
            local_password=self.local_password
        ).result()

        res_wallet_init = self.t.wallet_init(
            public_key=res_decrypt_key['public_key'],
            secret=res_decrypt_key['secret']
        ).result()

        self.assertIsInstance(res_wallet_init, dict)
        self.assertEqual('ok', res_wallet_init['@type'])

        res_delete_new_key = self.t.delete_key(
            public_key=res_create_new_key['public_key'],
            secret=res_create_new_key['secret']
        ).result()
        self.assertIsInstance(res_delete_new_key, dict)
        self.assertNotEqual('error', res_delete_new_key['@type'])

        # don't forget to delete decrypted key too because there is no method to decrypt key only in memory
        res_delete_decrypted_key = self.t.delete_key(
            public_key=res_decrypt_key['public_key'],
            secret=res_decrypt_key['secret']
        ).result()
        self.assertIsInstance(res_delete_decrypted_key, dict)
        self.assertNotEqual('error', res_delete_decrypted_key['@type'])

    def test_testgiver_address_new_transaction(self):
        """
            Reference implementation of wallet operation using testgiver_ and test_wallet_ funcs. Due to asynchronous nature of TON the rest of test
            cannot be done at the moment of faucet exhaustion. Waiting for a new faucet address & and Grams on it :)
        """
        # create key
        res_create_new_key = self.t.create_new_key(
            local_password=self.local_password,
            mnemonic=self.mn_phrase
        ).result()
        self.assertIsInstance(res_create_new_key, dict)
        self.assertNotEqual('error', res_create_new_key['@type'])

        # decrypt key to public key & secret
        res_decrypt_key = self.t.decrypt_key(
            public_key=res_create_new_key['public_key'],
            secret=res_create_new_key['secret'],
            local_password=self.local_password
        ).result()
        self.assertIsInstance(res_create_new_key, dict)
        self.assertNotEqual('error', res_decrypt_key['@type'])

        # convert public key to account address (testing in 0 chain)
        res_wallet_account_address = self.t.wallet_get_account_address(
            public_key=res_decrypt_key['public_key']
        ).result()
        self.assertIsInstance(res_wallet_account_address, dict)
        self.assertNotEqual('error', res_wallet_account_address['@type'])
        self.assertEqual('accountAddress', res_wallet_account_address['@type'])
        account_address = res_wallet_account_address['account_address']

        # get current state of faucet (we need seq number)
        res_testgiver_account_state = self.t.testgiver_getaccount_state().result()
        self.assertIsInstance(res_testgiver_account_state, dict)
        self.assertEqual('testGiver.accountState', res_testgiver_account_state['@type'])

        # send grams from faucet to uninitialized wallet
        res_testgiver_send_grams = self.t.testgiver_send_grams(
            dest_address=account_address,
            seq_no=res_testgiver_account_state['seqno'],
            amount=int(1 * 10e8)
        ).result()
        self.assertIsInstance(res_testgiver_send_grams, dict)
        self.assertNotEqual('error', res_testgiver_send_grams['@type'])
        self.assertEqual('sendGramsResult', res_testgiver_send_grams['@type'])

        # init new test wallet specified by public key & secret
        res_test_wallet_init = self.t.wallet_init(
            public_key=res_decrypt_key['public_key'],
            secret=res_decrypt_key['secret']
        ).result()
        self.assertIsInstance(res_test_wallet_init, dict)
        self.assertNotEqual('error', res_test_wallet_init['@type'])
        self.assertEqual('ok', res_test_wallet_init['@type'])

        res_test_wallet_get_account_state = self.t.wallet_get_account_state(
            address=account_address
        ).result()
        self.assertIsInstance(res_test_wallet_get_account_state, dict)
        # self.assertNotEqual('error', res_test_wallet_init['@type'])

        res_delete_new_key = self.t.delete_key(
            public_key=res_create_new_key['public_key'],
            secret=res_create_new_key['secret']
        ).result()
        self.assertIsInstance(res_delete_new_key, dict)
        self.assertNotEqual('error', res_delete_new_key['@type'])

        # don't forget to delete decrypted key too because there is no method to decrypt key only in memory
        res_delete_decrypted_key = self.t.delete_key(
            public_key=res_decrypt_key['public_key'],
            secret=res_decrypt_key['secret']
        ).result()
        self.assertIsInstance(res_delete_decrypted_key, dict)
        self.assertNotEqual('error', res_delete_decrypted_key['@type'])
