#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from time import sleep as callback_function
from doorpi.action.base import SingleAction

def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) is not 1: return None

    time = float(parameter_list[0])

    return SleepAction(callback_function, time)

class SleepAction(SingleAction):
    pass