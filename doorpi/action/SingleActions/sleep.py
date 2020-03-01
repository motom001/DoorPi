# -*- coding: utf-8 -*-
from doorpi.action.base import SingleAction

from time import sleep as callback_function

import logging
logger = logging.getLogger(__name__)
logger.debug('%s loaded', __name__)


def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) is not 1:
        return None

    time = float(parameter_list[0])
    return SleepAction(callback_function, time)

class SleepAction(SingleAction):
    pass
