#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from doorpi.action.base import SingleAction
import doorpi

from time import sleep

def sipphone_calltimeout(timeout, *callstate_to_check):
    #import pjsua
    try:
        doorpi.DoorPi().sipphone.lib.thread_register('pjsip_handle_events')
        return doorpi.DoorPi().sipphone.call_timeout(timeout, callstate_to_check)
    except:
        return False

def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) < 1: return None

    timeout = int(parameter_list[0])
    callstate_to_check = parameter_list[1:]

    return SipphoneCallTimeoutAction(sipphone_calltimeout, timeout = timeout)

class SipphoneCallTimeoutAction(SingleAction):
    pass
