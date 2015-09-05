#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from doorpi.keyboard.AbstractBaseClass import KeyboardAbstractBaseClass, HIGH_LEVEL, LOW_LEVEL
import doorpi

def get(**kwargs): return DUMMY(**kwargs)
class DUMMY(KeyboardAbstractBaseClass):
    name = 'DUMMY Keyboard'

    def __init__(self, input_pins, output_pins, keyboard_name, bouncetime = 200, polarity = 0, *args, **kwargs):
        logger.debug("__init__(input_pins = %s, output_pins = %s, bouncetime = %s, polarity = %s)",
                     input_pins, output_pins, bouncetime, polarity)

        conf_pre = kwargs['conf_pre']
        conf_post = kwargs['conf_post']

        self.keyboard_name = keyboard_name
        self._polarity = polarity
        self._InputPins = doorpi.DoorPi().config.get_keys(conf_pre+'InputPins'+conf_post)
        self._OutputPins = doorpi.DoorPi().config.get_keys(conf_pre+'OutputPins'+conf_post)

        for output_pin in self._OutputPins:
            self.set_output(output_pin, 0, False)

        self.register_destroy_action()

    def destroy(self):
        if self.is_destroyed: return

        logger.debug("destroy")
        # shutdown all output-pins
        for output_pin in self._OutputPins:
            self.set_output(output_pin, 0, False)
        doorpi.DoorPi().event_handler.unregister_source(__name__, True)
        self.__destroyed = True

    def status_input(self, pin):
        if self._polarity is 0:
            return str(0).lower() in HIGH_LEVEL
        else:
            return str(0).lower() in LOW_LEVEL

    def set_output(self, pin, value, log_output = True):
        parsed_pin = doorpi.DoorPi().parse_string("!"+str(pin)+"!")
        if parsed_pin != "!"+str(pin)+"!":
            pin = parsed_pin

        value = str(value).lower() in HIGH_LEVEL
        if self._polarity is 1: value = not value
        log_output = str(log_output).lower() in HIGH_LEVEL

        if pin not in self._OutputPins: return False
        if log_output: logger.debug("out(pin = %s, value = %s, log_output = %s)", pin, value, log_output)

        self._OutputStatus[pin] = value
        return True
