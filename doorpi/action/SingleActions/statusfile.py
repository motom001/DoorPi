#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from action.base import SingleAction
import doorpi

def write_statusfile(filename, filecontent):
    try:
        filename = doorpi.DoorPi().parse_string(filename)
        filecontent = doorpi.DoorPi().parse_string(filecontent)
    except:
        logger.warning("while action statusfile - error to get DoorPi().parse_string")
        return False

    try:
        file = open(filename, 'w')
        try:
            file.write(filecontent)
            file.flush()
        finally:
            file.close()
    except IOError as e:
        logger.warning("while action statusfile - I/O error(%s): %s"%(e.errno, e.strerror))
        return False

    return True

def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) < 2: return None

    filename = parameter_list[0]
    filecontent = ''.join(parameter_list[1:])

    return SleepAction(write_statusfile, filename, filecontent)

class SleepAction(SingleAction):
    pass