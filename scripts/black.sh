#!/usr/bin/env bash

set -e

export PATH=env/bin:${PATH}

pip install black==18.9b0

black tests ipc_unix setup.py --check
