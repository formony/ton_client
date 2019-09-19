# -*- coding: utf-8 -*-

import unittest
from ton_client.tonlib import Tonlib


class ConfigMixture:

    config_ls = '''
        {
          "liteservers": [
            {
              "ip": 1137658550,
              "port": 4924,
              "id": {
                "@type": "pub.ed25519",
                "key": "peJTw/arlRfssgTuf9BMypJzqOi7SXEqSPSWiEw2U1M="
              }
            }
          ],
          "validator": {
            "@type": "validator.config.global",
            "zero_state": {
              "workchain": -1,
              "shard": -9223372036854775808,
              "seqno": 0,
              "root_hash": "VCSXxDHhTALFxReyTZRd8E4Ya3ySOmpOWAS4rBX9XBY=",
              "file_hash": "eh9yveSz1qMdJ7mOsO+I+H77jkLr9NpAuEkoJuseXBo="
            }
          }
        }
    '''


class TonlibTestCase1(unittest.TestCase, ConfigMixture):
    def test_lib_init(self):
        data = {
            '@type': 'init',
            'options': {
                '@type': 'options',
                'config': self.config_ls,
                'keystore_directory': '/'
            }
        }
        lib = Tonlib()
        r = lib.ton_async_execute(data)
        self.assertIsInstance(r, dict)
        self.assertEqual('ok', r['@type'])


class TonlibTestCase2(unittest.TestCase, ConfigMixture):
    @classmethod
    def setUpClass(cls) -> None:

        data = {
            '@type': 'init',
            'options': {
                '@type': 'options',
                'config': cls.config_ls,
                'keystore_directory': '/'
            }
        }
        lib = cls.lib = Tonlib()
        lib.ton_async_execute(data)

    def test_lib_local_ops(self):
        data = {
            '@type': 'testGiver.getAccountAddress'
        }
        self.lib.ton_send(data)
        r = self.lib.ton_receive()
        self.assertIsInstance(r, dict)
        self.assertEqual('Ef+BVndbeTJeXWLnQtm5bDC2UVpc0vH2TF2ksZPAPwcODSkb', r['account_address'])

    def test_lib_remote_ops(self):
        data = {
            '@type': 'raw.getAccountState',
            'account_address': {'account_address': 'Ef+BVndbeTJeXWLnQtm5bDC2UVpc0vH2TF2ksZPAPwcODSkb'}
        }
        r = self.lib.ton_async_execute(data)
        self.assertIsInstance(r, dict)
        self.assertIn('balance', r)


if __name__ == '__main__':
    unittest.main()
