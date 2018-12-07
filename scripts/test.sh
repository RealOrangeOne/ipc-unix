#!/usr/bin/env bash

set -e

export PATH=env/bin:${PATH}

nose2 $@ -C --coverage ipc_unix

black tests ipc_unix setup.py --check
flake8 ipc_unix tests setup.py --ignore=E128,E501
isort -rc -c ipc_unix tests setup.py
mypy --strict-optional ipc_unix tests
