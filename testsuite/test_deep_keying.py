# -*- coding: utf-8 -*-

import unittest
import os
import hashlib
import base64

from ton_client.client import TonlibClientFutures

proj_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')


class KeyingPrimitivesTestCase(unittest.TestCase):
    keystore = os.path.join(proj_path, 'tmp')
    password = 'sdfhtyjukteradfcvbnhgyutg'
    salt = 'kiuthkiukhmvncbxgfsryturyitukGRETRTUYKYTFDH'
    PBKDF_ITERATIONS = 100000
    t = TonlibClientFutures(keystore=keystore)

    def test_kdf_1(self):
        password = bytes(self.password, 'utf-8')
        salt = bytes(self.salt, 'utf-8')
        local_kdf = hashlib.pbkdf2_hmac('sha512', password, salt, self.PBKDF_ITERATIONS)
        local_kdf = base64.b64encode(local_kdf)

        remote_kdf_res = self.t.external_kdf(password=self.password, salt=self.salt, iterations=self.PBKDF_ITERATIONS).result()
        remote_kdf = bytes(remote_kdf_res['bytes'], 'utf-8')

        self.assertEqual(local_kdf, remote_kdf)


if __name__ == '__main__':
    unittest.main()
