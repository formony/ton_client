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


def threaded(f):
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

    @threaded
    def testgiver_getaccount_address(self):
        data = {
            '@type': 'testGiver.getAccountAddress'
        }
        r = self._t_local.tonlib.ton_async_execute(data)
        return r

    @threaded
    def testgiver_getaccount_state(self):
        data = {
            '@type': 'testGiver.getAccountState'
        }
        r = self._t_local.tonlib.ton_async_execute(data)
        return r


class TonlibClientFutures(TonlibClientBase):
    _style = 'futures'


class TonlibClientAsyncio(TonlibClientBase):
    _style = 'asyncio'
