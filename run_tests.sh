#!/bin/bash

. bin/create_and_enter_virtualenv.sh

PYTHONPATH=.:src python -m unittest discover
exit $?
