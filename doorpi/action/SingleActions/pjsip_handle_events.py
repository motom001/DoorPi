import doorpi
from doorpi.action.base import SingleAction

import logging
logger = logging.getLogger(__name__)
logger.debug('%s loaded', __name__)


def pjsip_handle_events(timeout):
    doorpi.DoorPi().sipphone.self_check(timeout)


def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) != 1:
        return None

    timeout = int(parameter_list[0])
    return PjsipHandleEventsAction(pjsip_handle_events, timeout=timeout)


class PjsipHandleEventsAction(SingleAction):
    pass
