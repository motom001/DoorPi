#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from action.base import SingleAction
import doorpi

def pjsip_handle_events(timeout):
    try:
        doorpi.DoorPi().sipphone.self_check(timeout)
    except KeyboardInterrupt:
        logger.info("Detected KeyboardInterrupt and shutdown DoorPi")
        doorpi.DoorPi().destroy()

def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) is not 1: return None

    timeout = int(parameter_list[0])

    return PjsipHandleEventsAction(pjsip_handle_events, timeout = timeout)

class PjsipHandleEventsAction(SingleAction):
    pass
