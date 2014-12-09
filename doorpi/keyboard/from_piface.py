#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from keyboard.base import keyboard

import piface.pfio # basic for PiFce control
from time import sleep # used by: PiFace.set_output
import sys # used by: PiFace.self_test to catch exception and show errormessage

class PiFace(keyboard):

    __InputPins = [0,1,2,3,4,5,6,7]
    __OutputPins = [0,1,2,3,4,5,6,7]

    __last_key = None
    def get_last_key(self):
        return self.__last_key

    def __init__(self, input_pins = [0,1,2,3,4,5,6,7], output_pins = [0,1,2,3,4,5,6,7]):
        logger.debug("__init__(input_pins = %s, output_pins = %s)", input_pins, output_pins)
        self.__InputPins = [int(i) for i in input_pins]
        self.__OutputPins = [int(i) for i in output_pins]
        piface.pfio.init()

    def __del__(self):
        self.destroy()

    def destroy(self):
        logger.debug("destroy")
        # shutdown all output-pins
        for x in range(len(self.__OutputPins)):
            self.set_output(self.__OutputPins[x], 0, 0, 0.0)

    def self_test(self):
        try:
            logger.debug("self_test()")
            logger.info("Check InputPins: %s", self.__InputPins)
            pressed_keys = self.which_keys_are_pressed()
            if pressed_keys:
                logger.warning("Key(s) pressed while init -> why? -- \r\n %s", '-- \r\n'.join(pressed_keys))

            logger.info("Check OutputPins: %s", self.__OutputPins)
            for x in range(len(self.__OutputPins)):
                self.set_output(self.__OutputPins[x], 1, 0, 0.1)
        except:
            logger.critical("Unexpected error: %s",str(sys.exc_info()[0]))
            return False
        else:
            logger.info("self_test success")
            return True

    def which_keys_are_pressed(self):
        pressed_keys = []
        for x in range(len(self.__InputPins)):
            if (piface.pfio.digital_read(self.__InputPins[x]) == 1):
                return_list.append("Key: "+str(x)+" Pin: "+str(self.__InputPins[x]))

        logger.trace("which_keys_are_pressed return "+str(pressed_keys))
        return pressed_keys

    def is_key_pressed(self):
        for pin in self.__InputPins:
            if piface.pfio.digital_read(pin) == 1:
                logger.trace("is_key_pressed return key %s",str(pin))
                self.__last_key = pin
                return pin
        return None

    def set_output(self, pin, start_value = 1, end_value = 0, timeout = 0.5, stop_pin = None, log_output = True):
        if not pin in self.__OutputPins: return False
        if log_output:
            logger.debug(
                "set_output (pin = %s, start_value = %s, end_value = %s, timeout = %s, stop_pin = %s)",
                pin, start_value, end_value, timeout, stop_pin
            )

        piface.pfio.digital_write(pin, start_value)
        if timeout < 0.1:
            sleep(timeout)
        else:
            total_time = 0
            while total_time <= timeout:
                total_time += 0.1
                if stop_pin in self.__InputPins and piface.pfio.digital_read(stop_pin) == 1:
                    logger.debug('stop pin pressed -> break action')
                    break
                sleep(0.1)

        piface.pfio.digital_write(pin, end_value)
        return True