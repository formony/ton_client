# -*- coding: utf-8 -*-

import base64
import asyncio
import struct

import crc16


def key_b64_to_hex_flip(b64_key):
    key_hex_unswaswapped_nibbles = base64.b64decode(b64_key).hex().upper()
    key_hex = "".join([f'{j}{i}' for i, j in zip(*[iter(key_hex_unswaswapped_nibbles)] * 2)])
    return key_hex


def coro_result(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def raw_to_userfriendly(address, tag=0x11):
    workchain_id, key = address.split(':')
    workchain_id = int(workchain_id)
    key = bytearray.fromhex(key)

    short_ints = [j * 256 + i for i, j in zip(*[iter(key)] * 2)]
    payload = struct.pack(f'bb{"H"*16}', tag, workchain_id, *short_ints)
    crc = crc16.crc16xmodem(payload)

    e_key = payload + struct.pack('>H', crc)
    return base64.b64encode(e_key).decode("utf-8")


def userfriendly_to_raw(address):
    k = base64.b64decode(address)[1:34]
    workchain_id = struct.unpack('b', k[:1])[0]
    key = k[1:].hex()
    return f'{workchain_id}:{key}'
