#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from doorpi.action.base import SingleAction
import doorpi


def call(number):
    doorpi.DoorPi().sipphone.call(number)

def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) is not 1: return None

    number = parameter_list[0]

    return CallAction(call, number = number)

class CallAction(SingleAction):
    pass
