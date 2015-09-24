#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.
set -x # Print commands and their arguments as they are executed.

if [[ $START_MODE = "application" ]]; then
    sudo doorpi_cli --trace --test
fi

if [[ $START_MODE = "daemon" ]]; then
    sudo service doorpi status
    sleep 5
    sudo service doorpi start
    sleep 5
    sudo service doorpi status
    sleep 5
    sudo service doorpi stop
    sleep 5
    sudo service doorpi status
fi
