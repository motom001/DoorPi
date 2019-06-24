"""The PJSUA2 SIP phone module for DoorPi."""

import logging

EVENT_SOURCE = __name__
logger = logging.getLogger(__name__)


def instantiate():
    from .glue import Pjsua2
    return Pjsua2()
