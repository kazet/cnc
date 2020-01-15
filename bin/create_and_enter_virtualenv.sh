#!/bin/bash

cd $(dirname "$0")

if [[ ! -e venv ]]; then
    virtualenv -p /usr/bin/python3.7 venv
fi

. venv/bin/activate
pip install -r requirements.txt

