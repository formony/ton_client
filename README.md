# ton_client

Python API client for blockchain [Telegram Open Network](https://test.ton.org/download.html)

[Website](https://www.formony.com/) | 
Telegram [News](https://t.me/Formony_news) | 
[Group](https://t.me/Formony_dev)   

[![CircleCI](https://img.shields.io/circleci/build/github/formony/ton_client)](https://circleci.com/gh/formony/ton_client)
[![Coverage](https://img.shields.io/codecov/c/github/formony/ton_client/master.svg)](https://codecov.io/gh/formony/ton_client)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-green.svg)](https://www.python.org/dev/peps/pep-0008/)

## Installation

This client works with Python 3.7 only.

Prerequisites: 
* [Pipfile](https://github.com/pypa/pipfile)

* ton_client is been shipped with prebuilt fullnode's client library for Ubuntu Xenial & latest macOS. 
In case of incompatibility with your distro it's needed to build TON fullnode's libtonlibjson.so / libtonlibjson.dylib depends on archtecture. 
Check [here](https://github.com/formony/ton_client/tree/master/docs/ton.md) for fullnode's build instructions.
Don't forget to copy library file to ton_client/distlib/linux/libtonlibjson.so or ton_client/distlib/darwin/libtonlibjson.dylib

ton_client hasn't been published to PyPI yet so build and install it on your own:

`git clone https://github.com/formony/ton_client.git`

`make setup-all && python ./setup.py install`

## To be done

* [x] parallel multithreading calling of libtonlibjson. Note: there is no GIL problem due using ctypes.CDLL()
* [ ] support all the funcs of libtonlibjson as described in [spec](https://github.com/formony/ton_client/tree/master/docs/tonlib_api.tl) and mirror [here](https://github.com/ton-blockchain/ton/blob/master/tl/generate/scheme/tonlib_api.tl). TL itself described [here](https://core.telegram.org/mtproto/TL)
* [x] asyncio wrapper
* [ ] support smart contracts build
* [ ] crypto primitives to work with plain keys
* [x] support of BIP32 mnemonic (see testsuite)
* [ ] support key derivation as in BIP44 
 