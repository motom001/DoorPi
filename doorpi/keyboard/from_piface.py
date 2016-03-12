#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import pifacedigitalio as p  # basic for PiFce control
from doorpi.keyboard.AbstractBaseClass import KeyboardAbstractBaseClass, HIGH_LEVEL, LOW_LEVEL
import doorpi


def get(**kwargs): return PiFace(**kwargs)


class PiFace(KeyboardAbstractBaseClass):

    def __init__(self, input_pins, output_pins, keyboard_name, bouncetime,
                 polarity=0, pressed_on_key_down=True, *args, **kwargs):
        logger.debug("__init__(input_pins = %s, output_pins = %s, polarity = %s)",
                     input_pins, output_pins, polarity)
        self.keyboard_name = keyboard_name
        self._polarity = polarity
        self._InputPins = map(int, input_pins)
        self._OutputPins = map(int, output_pins)
        self._pressed_on_key_down = pressed_on_key_down

        p.init()
        self.__listener = p.InputEventListener()
        for input_pin in self._InputPins:
            self.__listener.register(
                pin_num=input_pin,
                direction=p.IODIR_BOTH,
                callback=self.event_detect,
                settle_time=bouncetime / 1000  # from milliseconds to seconds
            )
            self._register_EVENTS_for_pin(input_pin, __name__)
        self.__listener.activate()

        # use set_output to register status @ dict self.__OutputStatus
        for output_pin in self._OutputPins:
            self.set_output(output_pin, 0, False)

        self.register_destroy_action()

    def destroy(self):
        if self.is_destroyed:
            return
        logger.debug("destroy")
        
        # shutdown listener
        self.__listener.deactivate()
        
        # shutdown all output-pins
        for output_pin in self._OutputPins:
            self.set_output(output_pin, 0, False)
        p.deinit()
        doorpi.DoorPi().event_handler.unregister_source(__name__, True)
        self.__destroyed = True

    def event_detect(self, event):
        if self.status_input(event.pin_num):
            self._fire_OnKeyDown(event.pin_num, __name__)
            if self._pressed_on_key_down:  # issue 134
                self._fire_OnKeyPressed(event.pin_num, __name__)
        else:
            self._fire_OnKeyUp(event.pin_num, __name__)
            if not self._pressed_on_key_down:  # issue 134
                self._fire_OnKeyPressed(event.pin_num, __name__)

    def status_input(self, pin):
        if self._polarity is 0:
            return str(p.digital_read(int(pin))).lower() in HIGH_LEVEL
        else:
            return str(p.digital_read(int(pin))).lower() in LOW_LEVEL

    def set_output(self, pin, value, log_output = True):
        parsed_pin = doorpi.DoorPi().parse_string("!"+str(pin)+"!")
        if parsed_pin != "!"+str(pin)+"!":
            pin = parsed_pin

        pin = int(pin)
        value = str(value).lower() in HIGH_LEVEL
        if self._polarity is 1: value = not value
        log_output = str(log_output).lower() in HIGH_LEVEL

        if not pin in self._OutputPins: return False
        if log_output: logger.debug("out(pin = %s, value = %s, log_output = %s)", pin, value, log_output)

        p.digital_write(pin, value)
        self._OutputStatus[pin] = value
        return True
