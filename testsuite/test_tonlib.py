# -*- coding: utf-8 -*-

import unittest
import struct
import socket
import os

import ujson as json

from ton_client.tonlib import Tonlib
from ton_client.utils import raw_to_userfriendly


class ConfigMixture:
    ip = '67.207.74.182'
    port = 4924
    key = 'peJTw/arlRfssgTuf9BMypJzqOi7SXEqSPSWiEw2U1M='
    proj_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
    keystore = os.path.join(proj_path, 'tmp')

    config_ls_obj = {
        '@type': 'liteserver.desc',
        'ip': struct.unpack('!I', socket.inet_aton(ip))[0],
        'port': port,
        'id': {
            '@type': 'pub.ed25519',
            'key': key
        }
    }
    config_vl_obj = {
        '@type': 'validator.config.global',
        'zero_state': {
            'workchain': -1,
            'shard': -9223372036854775808,
            'seqno': 0,
            'root_hash': 'VCSXxDHhTALFxReyTZRd8E4Ya3ySOmpOWAS4rBX9XBY=',
            'file_hash': 'eh9yveSz1qMdJ7mOsO+I+H77jkLr9NpAuEkoJuseXBo='
        }
    }
    config_obj = {
        'liteservers': [
            config_ls_obj
        ],
        'validator': config_vl_obj
    }

    keystore_obj = {
        '@type': 'keyStoreTypeDirectory',
        'directory': keystore
    }
    init_obj = {
        '@type': 'init',
        'options': {
            '@type': 'options',
            'config': {
                '@type': 'config',
                'config': json.dumps(config_obj)
            },
            'keystore_type': keystore_obj
        }
    }


class TonlibTestCase1(unittest.TestCase, ConfigMixture):
    def test_lib_init(self):
        lib = Tonlib()
        r = lib.ton_async_execute(self.init_obj)
        self.assertIsInstance(r, dict)
        self.assertEqual('ok', r['@type'])


class TonlibTestCase2(unittest.TestCase, ConfigMixture):
    testgiver_address = raw_to_userfriendly('-1:FCB91A3A3816D0F7B8C2C76108B8A9BC5A6B7A55BD79F8AB101C52DB29232260', 0x91)

    @classmethod
    def setUpClass(cls) -> None:

        lib = cls.lib = Tonlib()
        lib.ton_async_execute(cls.init_obj)

    def test_lib_local_ops(self):
        data = {
            '@type': 'testGiver.getAccountAddress'
        }
        self.lib.ton_send(data)
        r = self.lib.ton_receive()
        self.assertIsInstance(r, dict)
        self.assertEqual(self.testgiver_address, r['account_address'])

    def test_lib_remote_ops(self):
        data = {
            '@type': 'raw.getAccountState',
            'account_address': {'account_address': self.testgiver_address}
        }
        r = self.lib.ton_async_execute(data)
        self.assertIsInstance(r, dict)
        self.assertIn('balance', r)


if __name__ == '__main__':
    unittest.main()
