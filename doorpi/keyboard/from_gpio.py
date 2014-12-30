#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from keyboard.AbstractBaseClass import KeyboardAbstractBaseClass

import RPi.GPIO as RPiGPIO
from time import sleep # used by: GPIO.set_output
import sys # used by: GPIO.self_test to catch exception and show errormessage

class GPIO(KeyboardAbstractBaseClass):
    name = 'GPIO Keyboard'

    __InputPins = [11]
    __OutputPins = [16]

    __last_key = None
    def get_last_key(self):
        return self.__last_key

    def __init__(self, input_pins = [11], output_pins = [16]):
        logger.debug("GPIO.__init__(input_pins = %s, output_pins = %s)", input_pins, output_pins)
        self.__InputPins = map(int, input_pins)
        self.__OutputPins = map(int, output_pins)
        RPiGPIO.setmode(RPiGPIO.BCM)
        for x in self.__InputPins:
            RPiGPIO.setup(x, RPiGPIO.IN)

        for x in self.__OutputPins:
            RPiGPIO.setup(x, RPiGPIO.OUT)

    def __del__(self):
        self.destroy()

    def destroy(self):
        logger.debug("GPIO.destroy()")
        RPiGPIO.cleanup()

    def self_test(self):
        try:
            logger.debug("GPIO.self_test()")
            logger.info("Check InputPins: %s", self.__InputPins)
            pressed_keys = self.which_keys_are_pressed()
            if pressed_keys:
                logger.warning("Key(s) pressed while init -> why? -- \r\n %s", '-- \r\n'.join(pressed_keys))

            logger.info("Check OutputPins: %s", self.__OutputPins)
            for x in self.__OutputPins:
                self.set_output(x, 1, 0, 0.1)
        except:
            logger.critical("Unexpected error: %s",str(sys.exc_info()[0]))
            return False
        else:
            logger.info("self_test for GPIO success")
            return True

    def which_keys_are_pressed(self):
        pressed_keys = []
        for x in self.__InputPins:
            if RPiGPIO.input(x):
                return_list.append("Key: "+str(x)+" Pin: "+str(self.__InputPins[x]))
        return pressed_keys

    def is_key_pressed(self):
        for x in self.__InputPins:
            if RPiGPIO.input(x):
                logger.trace("GPIO.is_key_pressed return "+str(x))
                self.__last_key = x
                return x
        return None

    def set_output(self, pin, start_value = 1, end_value = 0, timeout = 0.5, stop_pin = None, log_output = True):
        if not pin in self.__OutputPins: return False
        if log_output:
            logger.debug(
                "set_output (pin = %s, start_value = %s, end_value = %s, timeout = %s, stop_pin = %s)",
                pin, start_value, end_value, timeout, stop_pin
            )

        RPiGPIO.output(pin, start_value)
        if timeout < 0.1:
            sleep(timeout)
        else:
            total_time = 0
            while total_time <= timeout:
                total_time += 0.1
                if stop_pin in self.__InputPins and RPiGPIO.input(self.__InputPins[stop_pin]) == 1:
                    logger.debug('stop pin pressed -> break action')
                    break
                sleep(0.1)

        RPiGPIO.output(pin, end_value)
        return True
