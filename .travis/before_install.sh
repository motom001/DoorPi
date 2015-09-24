#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.
set -x # Print commands and their arguments as they are executed.

pip install --upgrade pip
pip uninstall -y setuptools
sudo rm -f /usr/local/lib/python2.7/dist-packages/setuptools-12.0.5-py2.7.egg
pip install --upgrade setuptools
