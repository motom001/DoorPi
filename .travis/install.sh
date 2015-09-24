#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.
set -x # Print commands and their arguments as they are executed.

if [[ $START_MODE = "application" ]]; then
    python setup.py install
fi

if [[ $START_MODE = "daemon" ]]; then
    sudo -H python setup.py install
fi
