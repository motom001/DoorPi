#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import doorpi.action.base
import time
from doorpi import DoorPi

class SingleAction(SingleActionBaseClass):

    __led = None

    def is_alive_led(self, led):
        # blink, status led, blink
        if int(round(time.time())) % 2:
            DoorPi().get_keyboard.set_output(
                pin = led,
                start_value = 1,
                end_value = 1,
                timeout = 0.0,
                log_output = False
            )
        else:
            DoorPi().get_keyboard.set_output(
                pin = led,
                start_value = 0,
                end_value = 0,
                timeout = 0.0,
                log_output = False
            )

    def fire(self):
        self.is_alive_led(self.__led)