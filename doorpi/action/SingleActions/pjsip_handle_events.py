#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from action.base import SingleAction
import doorpi

def pjsip_handle_events():
    doorpi.DoorPi().sipphone.self_check()

def get():
    return PjsipHandleEventsAction(pjsip_handle_events)

class PjsipHandleEventsAction(SingleAction):
    pass
