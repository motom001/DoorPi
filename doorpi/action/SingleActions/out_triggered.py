#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from time import sleep

from doorpi.action.base import SingleAction
import doorpi

def out_triggered(pin, start_value, end_value, timeout, stop_pin):
    doorpi.DoorPi().keyboard.set_output(pin, start_value)
    while timeout > 0 and stop_pin not in doorpi.DoorPi().keyboard.pressed_keys:
        sleep(0.1)
        timeout -= 0.1
    doorpi.DoorPi().keyboard.set_output(pin, end_value)
    return True

def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) is not 4 and not 5: return None

    pin = parameter_list[0]
    start_value = parameter_list[1]
    end_value = parameter_list[2]
    timeout = float(parameter_list[3])

    if len(parameters) == 5:
        stop_pin = parameter_list[4]
    else:
        stop_pin = 'NoStopPinSet'

    return OutTriggeredAction(out_triggered,
        pin = pin,
        start_value = start_value,
        end_value = end_value,
        timeout = timeout,
        stop_pin = stop_pin
    )

class OutTriggeredAction(SingleAction):
    pass
