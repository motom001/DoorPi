#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from doorpi.action.base import SingleAction

def log(message):
    logger.debug(message)

def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) is not 1: return None

    message = parameter_list[0]

    return LogAction(log, message)

class LogAction(SingleAction):
    pass