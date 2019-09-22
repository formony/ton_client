# -*- coding: utf-8 -*-

import struct
import socket
import logging
from concurrent.futures import ThreadPoolExecutor
import threading
import asyncio
import functools

import ujson as json
from .tonlib import Tonlib
from .utils import str_b64encode, raw_to_userfriendly

logger = logging.getLogger(__name__)


def parallelize(f):
    @functools.wraps(f)
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

        data = {
            '@type': 'init',
            'options': {
                '@type': 'options',
                'config': json.dumps(config_obj),
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
            internal.transactionId lt:int64 hash:bytes = internal.TransactionId;
        :return: dict as
            {
                '@type': 'testGiver.accountState',
                'seqno': int,
                'last_transaction_id': tbd!
            }
        """
        data = {
            '@type': 'testGiver.getAccountState'
        }
        r = self._t_local.tonlib.ton_async_execute(data)
        return r

    @parallelize
    def testgiver_send_grams(self, dest_address, seq_no, amount):
        """
        TL Spec:
            testGiver.sendGrams destination:accountAddress seqno:int32 amount:int64 = Ok;
            accountAddress account_address:string = AccountAddress;
        :param dest_address: str with raw or user friendly address
        :param seq_no: sequence number to gain consistency and prevent double spend
        :param amount: given simple fraction where 'amount' is numerator and 10e8 in denominator. E.g. amount = 6666000000 will be 6.66 Grams
        :return:
        """
        if len(dest_address.split(':')) == 2:
            dest_address = raw_to_userfriendly(dest_address)

        data = {
            '@type': 'testGiver.sendGrams',
            'seqno': seq_no,
            'amount': amount,
            'destination': {
                'account_address': dest_address
            }
        }

        r = self._t_local.tonlib.ton_async_execute(data)
        return r

    @parallelize
    def test_wallet_init(self, public_key, secret):
        """
        TL Spec:
            testWallet.init private_key:inputKey = Ok;
            key public_key:string secret:secureBytes = Key;
            inputKey key:key local_password:secureBytes = InputKey;
        :param public_key: str of base64 encoded public key as packed by e.g. create_new_key() or decrypt_key()
        :param secret: str of base64 encoded secret as packed by e.g. create_new_key() or decrypt_key()
        :return:
        """
        data = {
            '@type': 'testWallet.init',
            'private_key': {
                'key': {
                    'public_key': public_key,
                    'secret': secret
                }
            }
        }

        r = self._t_local.tonlib.ton_async_execute(data)
        return r

    @parallelize
    def test_wallet_get_account_address(self, public_key):
        """
        Specific method for getting address from public key. In contrast to Ethereum and many other blockchains,
        there is no 1-to-1 match between address and public key except this tonlib's internally hardcoded algorithm
        TL Spec:
            testWallet.getAccountState account_address:accountAddress = testWallet.AccountState;
            testWallet.accountState balance:int64 seqno:int32 last_transaction_id:internal.transactionId = testWallet.AccountState;
            internal.transactionId lt:int64 hash:bytes = internal.TransactionId;
            accountAddress account_address:string = AccountAddress;
        :param public_key: str of base64 encoded public key as packed by e.g. create_new_key() or decrypt_key()
        :return:
        """
        data = {
            '@type': 'testWallet.getAccountAddress',
            'initital_account_state': {
                'public_key': public_key
            }
        }

        r = self._t_local.tonlib.ton_async_execute(data)
        return r

    @parallelize
    def test_wallet_get_account_state(self, address: str):
        """
        TL Spec:
            testWallet.getAccountState account_address:accountAddress = testWallet.AccountState;
            testWallet.accountState balance:int64 seqno:int32 last_transaction_id:internal.transactionId = testWallet.AccountState;
            internal.transactionId lt:int64 hash:bytes = internal.TransactionId;
            accountAddress account_address:string = AccountAddress;
        :param address: str with raw or user friendly address
        :return:
        """
        if len(address.split(':')) == 2:
            address = raw_to_userfriendly(address)

        data = {
            '@type': 'testWallet.getAccountState',
            'account_address': {
                'account_address': address
            }
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
            'local_password': str_b64encode(local_password),
            'mnemonic_password': str_b64encode(' '.join(mnemonic)),
            'random_extra_seed': str_b64encode(random_extra_seed)
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
        :param public_key: str of base64 encoded public key as packed by e.g. create_new_key() or decrypt_key()
        :param secret: str of base64 encoded secret as packed by e.g. create_new_key() or decrypt_key()
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
                'local_password': str_b64encode(local_password),
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
        :param public_key: str of base64 encoded public key as packed by e.g. create_new_key() or decrypt_key()
        :param secret: str of base64 encoded secret as packed by e.g. create_new_key() or decrypt_key()
        :param local_password: string
        :param key_password: key to encrypt resulting PEM itself
        :return:
        """
        data = {
            '@type': 'exportPemKey',
            'key_password': str_b64encode(key_password),
            'input_key': {
                'local_password': str_b64encode(local_password),
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
        :param public_key: str of base64 encoded public key as packed by e.g. create_new_key() or decrypt_key()
        :param secret: str of base64 encoded secret as packed by e.g. create_new_key() or decrypt_key()
        :param local_password: string
        :param key_password: key to encrypt resulting PEM itself
        :return:
        """
        data = {
            '@type': 'exportEncryptedKey',
            'key_password': str_b64encode(key_password),
            'input_key': {
                'local_password': str_b64encode(local_password),
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
            'local_password': str_b64encode(local_password),
            'exported_key': {
                'type': 'exportedKey',
                'word_list': [str_b64encode(x) for x in mnemonic]
            },
            'mnemonic_password': str_b64encode(mnemonic_password)
        }

        r = self._t_local.tonlib.ton_async_execute(data)
        return r

    @parallelize
    def decrypt_key(self, public_key, secret, local_password):
        """
        Decrypt key encrypted with local_password and return secret & public key
        TL Spec:
            changeLocalPassword input_key:inputKey new_local_password:secureBytes = Key;
            key public_key:string secret:secureBytes = Key;
            inputKey key:key local_password:secureBytes = InputKey;

        :param public_key: str of base64 encoded public key as packed by e.g. create_new_key() or decrypt_key()
        :param secret: str of base64 encoded secret as packed by e.g. create_new_key() or decrypt_key()
        :param local_password: string
        :return: dict as
            {
                'public_key': base64 encoded string,
                'secret': base64 encoded string
            }
        """
        data = {
            '@type': 'changeLocalPassword',
            'input_key': {
                'local_password': str_b64encode(local_password),
                'key': {
                    'public_key': public_key,
                    'secret': secret
                }
            }

        }

        r = self._t_local.tonlib.ton_async_execute(data)
        return r


class TonlibClientFutures(TonlibClientBase):
    _style = 'futures'


class TonlibClientAsyncio(TonlibClientBase):
    _style = 'asyncio'
