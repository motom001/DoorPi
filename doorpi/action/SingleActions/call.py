#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from action.base import SingleAction
import doorpi


def call(Number):
    import pjsua
    doorpi.DoorPi().sipphone.call(Number)

def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) is not 1: return None

    number = parameter_list[0]

    return CallAction(call, Number = number)

class CallAction(SingleAction):
    pass
