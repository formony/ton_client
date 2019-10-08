# -*- coding: utf-8 -*-

from ctypes import CDLL, c_void_p, c_char_p, c_double
import json
import logging
import platform

import pkg_resources

logger = logging.getLogger(__name__)

LIB_PATH = './libtonlibjson.dylib'


def get_tonlib_path():
    arch_name = platform.system().lower()
    if arch_name == 'darwin':
        lib_name = 'libtonlibjson.dylib'
    elif arch_name == 'linux':
        lib_name = 'libtonlibjson.so'
    else:
        raise RuntimeError('Platform could not be identified')
    return pkg_resources.resource_filename(
        'ton_client',
        f'distlib/{arch_name}/{lib_name}'
    )


class Tonlib:
    def __init__(self, tonlib_path=get_tonlib_path()):
        tonlib = CDLL(tonlib_path)

        # load TDLib functions from shared library
        tonlib_json_client_create = tonlib.tonlib_client_json_create
        tonlib_json_client_create.restype = c_void_p
        tonlib_json_client_create.argtypes = []
        self._client = tonlib_json_client_create()

        tonlib_json_client_receive = tonlib.tonlib_client_json_receive
        tonlib_json_client_receive.restype = c_char_p
        tonlib_json_client_receive.argtypes = [c_void_p, c_double]
        self._tonlib_json_client_receive = tonlib_json_client_receive

        tonlib_json_client_send = tonlib.tonlib_client_json_send
        tonlib_json_client_send.restype = None
        tonlib_json_client_send.argtypes = [c_void_p, c_char_p]
        self._tonlib_json_client_send = tonlib_json_client_send

        tonlib_json_client_execute = tonlib.tonlib_client_json_execute
        tonlib_json_client_execute.restype = c_char_p
        tonlib_json_client_execute.argtypes = [c_void_p, c_char_p]
        self._tonlib_json_client_execute = tonlib_json_client_execute

        tonlib_json_client_destroy = tonlib.tonlib_client_json_destroy
        tonlib_json_client_destroy.restype = None
        tonlib_json_client_destroy.argtypes = [c_void_p]
        self._tonlib_json_client_destroy = tonlib_json_client_destroy

    def __del__(self):
        self._tonlib_json_client_destroy(self._client)

    def ton_send(self, query):
        query = json.dumps(query).encode('utf-8')
        self._tonlib_json_client_send(self._client, query)
        logging.debug(f'ton_send() with query \'{query}\'')

    def ton_receive(self, timeout=30.0):
        result = self._tonlib_json_client_receive(self._client, timeout)
        if result:
            result = json.loads(result.decode('utf-8'))
        logging.debug(f'ton_receive() with result \'{result}\'')
        return result

    def ton_async_execute(self, query, timeout=30.0):
        self.ton_send(query)
        return self.ton_receive(timeout)

    def ton_sync_execute(self, query):
        query = json.dumps(query).encode('utf-8')
        result = self._tonlib_json_client_execute(None, query)
        if result:
            result = json.loads(result.decode('utf-8'))
        logging.debug(f'ton_execute() with query \'{query}\' '
                      f'and result \'{result}\'')
        return result
