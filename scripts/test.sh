#!/usr/bin/env bash

set -e

export PATH=env/bin:${PATH}

python setup.py test

black tests ipc_unix
