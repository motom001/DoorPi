#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from action.base import SingleAction
import doorpi

def check_call_duration():
    doorpi.DoorPi().sipphone.check_call_duration()

def get():
    return CheckCallDurationAction(check_call_duration)

class CheckCallDurationAction(SingleAction):
    pass
