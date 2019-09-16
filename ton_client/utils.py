# -*- coding: utf-8 -*-

import base64
import asyncio


def key_b64_to_hex_flip(b64_key):
    key_hex_unswaswapped_nibbles = base64.b64decode(b64_key).hex().upper()
    key_hex = "".join([f'{j}{i}' for i, j in zip(*[iter(key_hex_unswaswapped_nibbles)] * 2)])
    return key_hex


def coro_result(coro):
    return asyncio.get_event_loop().run_until_complete(coro)
