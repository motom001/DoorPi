#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from action.base import SingleAction
import doorpi


def pjsip_handle_events(timeout):
    import pjsua
    doorpi.DoorPi().sipphone.lib.thread_register('pjsip_handle_events')
    doorpi.DoorPi().sipphone.lib.handle_events(timeout)

def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) is not 1: return None

    timeout = int(parameter_list[0])

    return PjsipHandleEventsAction(pjsip_handle_events, timeout = timeout)

class PjsipHandleEventsAction(SingleAction):
    pass
