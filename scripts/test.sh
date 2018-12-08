#!/usr/bin/env bash

set -e

export PATH=env/bin:${PATH}

nose2 $@ -C --coverage ipc_unix --verbose
