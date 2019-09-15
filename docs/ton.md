# TON fullnode build guide

Assume using Debian or Ubuntu

## Install requirements
`sudo apt install -y build-essential git cmake gperf zlib1g-dev libreadline-dev ccache libmicrohttpd-dev libssl-dev`

Where `zlib1g-dev` is a development package for zlib and `libssl-dev` stands for OpenSSL dev package.

### Buildin a right version of OpenSSL
Because TON itself depends on OpenSSL 1.0, it has to be built from sources.

`cd ~`

`wget https://www.openssl.org/source/openssl-1.0.2t.tar.gz`

`tar -xzf openssl-1.0.2t.tar.gz`

`mkdir ~/openssl-tree`

`cd ~/openssl-1.0.2t`

`./config --prefix=~/openssl-tree/ --openssldir=~/openssl-tree/`

`make -j12`

`make install`

## Cloning a repo

`git clone --recurse-submodules https://github.com/ton-blockchain/ton.git`


## Building

`mkdir ~/ton-build`

`cd ~/ton-build`

`OPENSSL_ROOT_DIR=~/openssl-tree/ cmake -DCMAKE_BUILD_TYPE=Release ../ton`

Prepare only necessary library:

`cmake --build . --target tonlibjson`

Or prepare everything:

`cmake --build . --target all`

Build:

`make -j12`

## Copying the result

`cp ~/ton-build/tonlib/libtonlibjson.0.5.dylib !!/ton_client/distlib/linux/libtonlibjson.so`
