#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import RPi.GPIO as RPiGPIO # basic for GPIO control
from doorpi.keyboard.AbstractBaseClass import KeyboardAbstractBaseClass, HIGH_LEVEL, LOW_LEVEL
import doorpi


def get(**kwargs): return GPIO(**kwargs)


class GPIO(KeyboardAbstractBaseClass):
    name = 'GPIO Keyboard'

    def __init__(self, input_pins, output_pins, conf_pre, conf_post, keyboard_name,
                 bouncetime=200, polarity=0, pressed_on_key_down=True, *args, **kwargs):
        logger.debug("__init__(input_pins = %s, output_pins = %s, bouncetime = %s, polarity = %s)",
                     input_pins, output_pins, bouncetime, polarity)
        self.keyboard_name = keyboard_name
        self._polarity = polarity
        self._InputPins = map(int, input_pins)
        self._OutputPins = map(int, output_pins)
        self._pressed_on_key_down = pressed_on_key_down

        RPiGPIO.setwarnings(False)

        section_name = conf_pre+'keyboard'+conf_post
        if doorpi.DoorPi().config.get(section_name, 'mode', "BOARD").upper() == "BOARD":
            RPiGPIO.setmode(RPiGPIO.BOARD)
        else:
            RPiGPIO.setmode(RPiGPIO.BCM)

        # issue 134
        pull_up_down = doorpi.DoorPi().config.get(section_name, 'pull_up_down', "PUD_OFF").upper()
        if pull_up_down == "PUD_DOWN":
            pull_up_down = RPiGPIO.PUD_DOWN
        elif pull_up_down == "PUD_UP":
            pull_up_down = RPiGPIO.PUD_UP
        else:
            pull_up_down = RPiGPIO.PUD_OFF

        # issue #133
        try:
            RPiGPIO.setup(self._InputPins, RPiGPIO.IN, pull_up_down=pull_up_down)
        except TypeError:
            logger.warning('you use an old version of GPIO library - fallback to single-register of input pins')
            for input_pin in self._InputPins:
                RPiGPIO.setup(input_pin, RPiGPIO.IN, pull_up_down=pull_up_down)

        for input_pin in self._InputPins:
            RPiGPIO.add_event_detect(
                input_pin,
                RPiGPIO.BOTH,
                callback=self.event_detect,
                bouncetime=int(bouncetime)
            )
            self._register_EVENTS_for_pin(input_pin, __name__)

        # issue #133
        try:
            RPiGPIO.setup(self._OutputPins, RPiGPIO.OUT)
        except TypeError:
            logger.warning('you use an old version of GPIO library - fallback to single-register of input pins')
            for output_pin in self._OutputPins:
                RPiGPIO.setup(output_pin, RPiGPIO.OUT)

        # use set_output to register status @ dict self._OutputStatus
        for output_pin in self._OutputPins:
            self.set_output(output_pin, 0, False)

        self.register_destroy_action()

    def destroy(self):
        if self.is_destroyed:
            return

        logger.debug("destroy")
        # shutdown all output-pins
        for output_pin in self._OutputPins:
            self.set_output(output_pin, 0, False)
        RPiGPIO.cleanup()
        doorpi.DoorPi().event_handler.unregister_source(__name__, True)
        self.__destroyed = True

    def event_detect(self, pin):
        if self.status_input(pin):
            self._fire_OnKeyDown(pin, __name__)
            if self._pressed_on_key_down:  # issue 134
                self._fire_OnKeyPressed(pin, __name__)
        else:
            self._fire_OnKeyUp(pin, __name__)
            if not self._pressed_on_key_down:  # issue 134
                self._fire_OnKeyPressed(pin, __name__)

    def status_input(self, pin):
        if self._polarity is 0:
            return str(RPiGPIO.input(int(pin))).lower() in HIGH_LEVEL
        else:
            return str(RPiGPIO.input(int(pin))).lower() in LOW_LEVEL

    def set_output(self, pin, value, log_output=True):
        parsed_pin = doorpi.DoorPi().parse_string("!"+str(pin)+"!")
        if parsed_pin != "!"+str(pin)+"!":
            pin = parsed_pin

        pin = int(pin)
        value = str(value).lower() in HIGH_LEVEL
        if self._polarity is 1:
            value = not value
        log_output = str(log_output).lower() in HIGH_LEVEL

        if pin not in self._OutputPins:
            return False
        if log_output:
            logger.debug("out(pin = %s, value = %s, log_output = %s)", pin, value, log_output)

        RPiGPIO.output(pin, value)
        self._OutputStatus[pin] = value
        return True
