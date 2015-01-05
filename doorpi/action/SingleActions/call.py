#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from action.base import SingleAction
import doorpi


def make_call(Number):
    import pjsua
    doorpi.DoorPi().sipphone.lib.thread_register('make_call_theard')
    doorpi.DoorPi().sipphone.make_call(Number)

def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) is not 1: return None

    number = parameter_list[0]

    return MakeCallAction(make_call, Number = number)

class MakeCallAction(SingleAction):
    pass
