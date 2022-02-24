import doorpi
from doorpi.action.base import SingleAction

import logging
logger = logging.getLogger(__name__)
logger.debug('%s loaded', __name__)


def call(number): doorpi.DoorPi().sipphone.call(number)


def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) != 1:
        return None

    number = parameter_list[0]
    return CallAction(call, number=number)


class CallAction(SingleAction):
    pass
