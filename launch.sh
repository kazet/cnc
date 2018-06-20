#!/bin/bash

cd $(dirname "$0")

. venv/bin/activate
export FLASK_APP=api.py
python -m flask run -h 0.0.0.0
