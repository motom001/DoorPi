#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from doorpi.action.base import SingleAction
import doorpi

def write_status_watchdog(watchdog_path, timeout):
    timeout = int(timeout)

    try:
        watchdog = open(watchdog_path, "w+")
    except:
        logger.warning("while action write_status_watchdog - error opening watchdog file")
        return False

    try:
        watchdog.write('\n')
        watchdog.flush()
    finally:
        watchdog.close()

    return True

def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) is not 1 and len(parameter_list) is not 2: return None

    watchdog = parameter_list[0]
    timeout = 5

    if len(parameter_list) is 2:
        timeout = int(parameter_list[1])

    return SleepAction(write_status_watchdog, watchdog, timeout)

class SleepAction(SingleAction):
    pass