#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.
set -x # Print commands and their arguments as they are executed.

sudo pip install --upgrade linphone4raspberry

if [[ $START_MODE = "application" ]]; then
    sudo mkdir /usr/local/etc/DoorPi && sudo chmod -R a+rw /usr/local/etc/DoorPi
    python setup.py install
fi

if [[ $START_MODE = "daemon" ]]; then
    sudo -H python setup.py install
fi
