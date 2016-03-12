#!/bin/bash

set -e # Exit immediately if a command exits with a non-zero status.
set -x # Print commands and their arguments as they are executed.

pip install --upgrade pip
pip --version
#pip uninstall -y setuptools
#sudo rm -f /usr/local/lib/python2.7/dist-packages/setuptools*.egg
pip install --upgrade setuptools
pip install linphone4raspberry
