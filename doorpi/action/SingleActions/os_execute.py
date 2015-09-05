#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import subprocess
from doorpi.action.base import SingleAction
import doorpi

def fire_command(command):
    return subprocess.Popen(
        command,
        shell = True,
        stdout = subprocess.PIPE
    ).stdout.read()

def get(parameters):
    parsed_parameters = doorpi.DoorPi().parse_string(parameters)
    return OsExecuteAction(fire_command, command = parsed_parameters)

class OsExecuteAction(SingleAction):
    pass