#!/usr/bin/env bash

set -e

export PATH=env/bin:${PATH}

black tests ipc_unix setup.py
isort -rc ipc_unix tests setup.py
