#!/bin/bash

#set -e # Exit immediately if a command exits with a non-zero status.
set -x # Print commands and their arguments as they are executed.

if [[ $START_MODE = "application" ]]; then
    sudo doorpi_cli --trace --test
fi

if [[ $START_MODE = "daemon" ]]; then
    sudo service doorpi status
    #if [ $? -ne 3 ] exit 1
    sleep 5
    sudo service doorpi start
    #if [ $? -ne 0 ] exit 1
    sleep 5
    sudo service doorpi status
    #if [ $? -ne 0 ] exit 1
    sleep 5
    sudo service doorpi stop
    #if [ $? -ne 0 ] exit 1
    sleep 5
    sudo service doorpi status
    #if [ $? -ne 3 ] exit 1
fi
