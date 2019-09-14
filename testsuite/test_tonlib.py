# -*- coding: utf-8 -*-

import struct
import socket
import ujson as json
import unittest
from ton_client.tonlib import Tonlib


class ConfigMixture:
    ip = '67.207.74.182'

    config_ls_obj = {
        'liteservers': [
            {
                '@type': 'liteserver.desc',
                'ip': struct.unpack('!I', socket.inet_aton(ip))[0],
                'port': 4924,
                'id': {
                    '@type': 'pub.ed25519',
                    'key': 'peJTw/arlRfssgTuf9BMypJzqOi7SXEqSPSWiEw2U1M='
                }
            }
        ]
    }
    config_ls = json.dumps(config_ls_obj)


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
        self.assertEqual(r['@type'], 'ok')


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
        self.assertEqual(r['account_address'], 'Ef+BVndbeTJeXWLnQtm5bDC2UVpc0vH2TF2ksZPAPwcODSkb')

    def test_lib_remote_ops(self):
        data = {
            '@type': 'raw.getAccountState',
            'account_address': {'account_address': 'Ef+BVndbeTJeXWLnQtm5bDC2UVpc0vH2TF2ksZPAPwcODSkb'}
        }
        r = self.lib.ton_async_execute(data)
        self.assertIn('balance', r)


if __name__ == '__main__':
    unittest.main()
