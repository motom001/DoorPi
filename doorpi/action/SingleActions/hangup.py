# -*- coding: utf-8 -*-
import doorpi
from doorpi.action.base import SingleAction

from time import sleep

import logging
logger = logging.getLogger(__name__)
logger.debug('%s loaded', __name__)


def hangup(waittime):
    if waittime > 0:
        logger.debug('Waiting %s seconds before sending hangup request', waittime)
        sleep(float(waittime))
    return doorpi.DoorPi().sipphone.hangup()

def get(parameters):
    if not parameters.isdigit(): 
        return None
    return HangupAction(hangup, parameters)


class HangupAction(SingleAction):
    pass
