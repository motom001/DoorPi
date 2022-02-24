import doorpi
from doorpi.action.base import SingleAction
from doorpi.action.SingleActions.out_triggered import get as fallback

import logging
logger = logging.getLogger(__name__)
logger.debug('%s loaded', __name__)


def get(parameters):
    parameter_list = parameters.split(',')
    # more than 3 parameters? 4. parameter should be timeout
    if len(parameter_list) > 3:
        return fallback(parameters)

    pin = parameter_list[0]
    value = parameter_list[1]

    # logging specified in action call?
    if len(parameter_list) == 2:
        log_output = True
    else:
        log_output = parameter_list[2]

    return OutAction(
        doorpi.DoorPi().keyboard.set_output,
        pin=pin,
        value=value,
        log_output=log_output
    )


class OutAction(SingleAction):
    pass
