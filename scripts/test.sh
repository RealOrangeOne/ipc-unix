#!/usr/bin/env bash

set -e

export PATH=env/bin:${PATH}

python setup.py test

black tests ipc_unix --check
flake8 ipc_unix tests --ignore=E128,E501
isort -rc -c ipc_unix tests
mypy --strict-optional ipc_unix tests
