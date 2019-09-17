# -*- coding: utf-8 -*-

import struct
import socket
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
import asyncio
import functools
from functools import wraps

import ujson as json
from .tonlib import Tonlib

logger = logging.getLogger(__name__)


def parallelize(f):
    @wraps(f)
    def wrapper(self, *args, **kwds):
        if self._style == 'futures':
            return self._executor.submit(f, self, *args, **kwds)
        if self._style == 'asyncio':
            loop = asyncio.get_event_loop()
            return loop.run_in_executor(self._executor, functools.partial(f, self, *args, **kwds))
        raise RuntimeError(self._style)
    return wrapper


class TonlibClientBase:
    _t_local = threading.local()
    _style = 'Choose asyncio or concurrent.futures style'

    def __init__(
            self,
            ip='67.207.74.182',
            port=4924,
            key='peJTw/arlRfssgTuf9BMypJzqOi7SXEqSPSWiEw2U1M=',
            keystore='./',
            threads=10
    ):
        self._executor = ThreadPoolExecutor(
            max_workers=threads,
            initializer=self.init_tonlib_thread,
            initargs=(ip, port, key, keystore)
        )

    def init_tonlib_thread(self, ip, port, key, keystore):
        """
        TL Spec
            init options:options = Ok;
            options config:string keystore_directory:string = Options;
        :param ip: IPv4 address in dotted notation
        :param port: IPv4 TCP port
        :param key: base64 pub key of liteserver node
        :param keystore: path to keystore on local filesystem
        :return: None
        """
        self._t_local.tonlib = Tonlib()
        config_ls_obj = {
            'liteservers': [
                {
                    '@type': 'liteserver.desc',
                    'ip': struct.unpack('!I', socket.inet_aton(ip))[0],
                    'port': port,
                    'id': {
                        '@type': 'pub.ed25519',
                        'key': key
                    }
                }
            ]
        }
        data = {
            '@type': 'init',
            'options': {
                '@type': 'options',
                'config': json.dumps(config_ls_obj),
                'keystore_directory': keystore
            }
        }

        r = self._t_local.tonlib.ton_async_execute(data)
        logging.debug(f'_init_lib() with query \'{data}\' and result {r}')

    @parallelize
    def testgiver_getaccount_address(self):
        """
        TL Spec:
            testGiver.getAccountAddress = AccountAddress;
            accountAddress account_address:string = AccountAddress;
        :return:
        """
        data = {
            '@type': 'testGiver.getAccountAddress'
        }
        r = self._t_local.tonlib.ton_async_execute(data)
        return r

    @parallelize
    def testgiver_getaccount_state(self):
        """
        TL Spec:
            testGiver.getAccountState = testGiver.AccountState;
            testGiver.accountState balance:int64 seqno:int32 last_transaction_id:internal.transactionId = testGiver.AccountState;
        :return:
        """
        data = {
            '@type': 'testGiver.getAccountState'
        }
        r = self._t_local.tonlib.ton_async_execute(data)
        return r

# TODO testGiver.sendGrams destination:accountAddress seqno:int32 amount:int64 = Ok;

    @parallelize
    def create_new_key(self, local_password, mnemonic, random_extra_seed=''):
        """
        TL Spec:
            createNewKey local_password:secureBytes mnemonic_password:secureBytes = Key;
            key public_key:bytes secret:secureBytes = Key;

        A new key will be stored locally (not at the litenode's fs) in keystore specified during __init__()
        :rtype: object
        :param local_password: string
        :param mnemonic: list[24] or list[16] of mnemonic words
        :return: dict as
            {
                '@type': 'key',
                'public_key': base64 string of byte[32],
                'secret': base64 string of byte[32]
            }
        """
        data = {
            '@type': 'createNewKey',
            'local_password': local_password,
            'mnemonic_password': ' '.join(mnemonic),
            'random_extra_seed': random_extra_seed
        }

        r = self._t_local.tonlib.ton_async_execute(data)
        return r

    @parallelize
    def delete_key(self, public_key):
        """
        TL Spec:
            deleteKey public_key:bytes = Ok;
        Key will be deleted from local fs (not at the litenode's fs) in keystore specified during __init__()
        :param public_key: base64 string of byte[32] of a public key
        :return: dict as
            {
                '@type': 'ok' | 'error',
            }
        """
        data = {
            '@type': 'deleteKey',
            'public_key': public_key
        }

        r = self._t_local.tonlib.ton_async_execute(data)
        return r

    @parallelize
    def export_key(self, public_key, secret, local_password):
        """
        TL Spec:
            exportKey input_key:inputKey = ExportedKey;
            inputKey key:key local_password:secureBytes = InputKey;
            key public_key:bytes secret:secureBytes = Key;
            exportedKey word_list:vector<secureString> = ExportedKey;
        :param public_key: base64 string of byte[32] of a public key
        :param secret: base64 string of byte[32] of a secret
        :param local_password: string
        :return: dict as
            {
                '@type': 'exportKey',
                'word_list': list[24] of mnemonic words
            }
        """

        data = {
            '@type': 'exportKey',
            'input_key': {
                'local_password': local_password,
                'key': {
                    'public_key': public_key,
                    'secret': secret
                }
            }
        }

        r = self._t_local.tonlib.ton_async_execute(data)
        return r

    @parallelize
    def export_pem_key(self, public_key, secret, local_password, key_password):
        """
        !Not supported yet!
         TL Spec:
            exportPemKey input_key:inputKey key_password:secureBytes = ExportedPemKey;
            inputKey key:key local_password:secureBytes = InputKey;
            key public_key:bytes secret:secureBytes = Key;
            exportedPemKey pem:secureString = ExportedPemKey;
        :param public_key: base64 string of byte[32] of a public key
        :param secret: base64 string of byte[32] of a secret
        :param local_password: string
        :param key_password: key to encrypt resulting PEM itself
        :return:
        """
        data = {
            '@type': 'exportPemKey',
            'key_password': key_password,
            'input_key': {
                'local_password': local_password,
                'key': {
                    'public_key': public_key,
                    'secret': secret
                }
            }
        }

        r = self._t_local.tonlib.ton_async_execute(data)
        return r

    @parallelize
    def export_encrypted_key(self, public_key, secret, local_password, key_password):
        """
         TL Spec:
            exportEncryptedKey input_key:inputKey key_password:secureBytes = ExportedEncryptedKey;
            inputKey key:key local_password:secureBytes = InputKey;
            key public_key:bytes secret:secureBytes = Key;
            exportedEncryptedKey data:secureBytes = ExportedEncryptedKey;
        :param public_key: base64 string of byte[32] of a public key
        :param secret: base64 string of byte[32] of a secret
        :param local_password: string
        :param key_password: key to encrypt resulting PEM itself
        :return:
        """
        data = {
            '@type': 'exportEncryptedKey',
            'key_password': key_password,
            'input_key': {
                'local_password': local_password,
                'key': {
                    'public_key': public_key,
                    'secret': secret
                }
            }
        }

        r = self._t_local.tonlib.ton_async_execute(data)
        return r

    @parallelize
    def import_key(self, local_password, mnemonic_password, mnemonic):
        """
        TL Spec:
            importKey local_password:secureBytes mnemonic_password:secureBytes exported_key:exportedKey = Key;
            exportedKey word_list: vector < secureString > = ExportedKey;

        :param local_password: string
        :param mnemonic_password: string
        :param mnemonic: list[24] of mnemonic words
        :return: dict as
            {
                '@type': 'key',
                'public_key': base64 string of byte[32],
                'secret': base64 string of byte[32]
            }
        """

        data = {
            '@type': 'importKey',
            'local_password': local_password,
            'exported_key': {
                'type': 'exportedKey',
                'word_list': mnemonic
            },
            'mnemonic_password': mnemonic_password
        }

        r = self._t_local.tonlib.ton_async_execute(data)
        return r


class TonlibClientFutures(TonlibClientBase):
    _style = 'futures'


class TonlibClientAsyncio(TonlibClientBase):
    _style = 'asyncio'
