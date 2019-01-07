#!/bin/bash

. bin/create_and_enter_virtualenv.sh

export FLASK_APP=src/server.py
PYTHONPATH=.:src python -m flask run -h 0.0.0.0
