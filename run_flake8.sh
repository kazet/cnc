#!/bin/bash

. bin/create_and_enter_virtualenv.sh

flake8
exit $?
