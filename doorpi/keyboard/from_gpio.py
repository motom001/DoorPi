#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import RPi.GPIO as RPiGPIO # basic for GPIO control

from keyboard.AbstractBaseClass import KeyboardAbstractBaseClass
import doorpi

class GPIO(KeyboardAbstractBaseClass):
    name = 'GPIO Keyboard'

    __InputPins = []
    @property
    def input_pins(self): return self.__InputPins
    __OutputPins = []
    @property
    def output_pins(self): return self.__OutputPins

    __OutputStatus = {}
    @property
    def output_status(self): return self.__OutputStatus

    __last_key = None
    @property

    def last_key(self):
        return self.__last_key

    def __init__(self, input_pins, output_pins, bouncetime = 5000):
        logger.debug("GPIO.__init__(input_pins = %s, output_pins = %s)", input_pins, output_pins)
        self.__InputPins = map(int, input_pins)
        self.__OutputPins = map(int, output_pins)

        doorpi.DoorPi().event_handler.register_event('OnKeyPressed', __name__)

        RPiGPIO.setmode(RPiGPIO.BOARD)

        RPiGPIO.setup(self.__InputPins, RPiGPIO.IN, pull_up_down = RPiGPIO.PUD_DOWN)
        for input_pin in self.__InputPins:
            RPiGPIO.add_event_detect(
                input_pin,
                RPiGPIO.RISING,
                callback = self.event_detect,
                bouncetime = bouncetime
            )
            doorpi.DoorPi().event_handler.register_event('OnKeyPressed_'+str(input_pin), __name__)

        RPiGPIO.setup(self.__OutputPins, RPiGPIO.OUT)
        #RPiGPIO.output(self.__OutputPins, RPiGPIO.LOW)
        # use set_output to register status @ dict self.__OutputStatus
        for output_pin in self.__OutputPins:
            self.set_output(output_pin, 0, False)

    def __del__(self):
        self.destroy()

    def destroy(self):
        logger.debug("GPIO.destroy()")
        # shutdown all output-pins
        for output_pin in self.__OutputPins:
            self.set_output(output_pin, 0, False)
        RPiGPIO.cleanup()
        doorpi.DoorPi().event_handler.unregister_source(__name__, True)

    def event_detect(self, pin):
        logger.trace('event_detect for %s', pin)
        self.__last_key = pin
        doorpi.DoorPi().event_handler('OnKeyPressed', __name__, {'pin': pin})
        doorpi.DoorPi().event_handler('OnKeyPressed_'+str(pin), __name__, {'pin': pin})

    def self_test(self):
        pass

    @property
    def pressed_keys(self):
        pressed_keys = []
        for input_pin in self.__InputPins:
            if self.status_inputpin(input_pin):
                pressed_keys.append(input_pin)
        #logger.trace("pressed_keys are %s" % pressed_keys)
        return pressed_keys

    @property
    def pressed_key(self):
        for input_pin in self.__InputPins:
            if self.status_inputpin(input_pin):
                logger.trace("pressed_key return key %s",str(input_pin))
                return input_pin
        return None

    def status_inputpin(self, pin):
        return RPiGPIO.input(pin)

    def status_output(self, pin):
        pin = int(pin)
        if not pin in self.__OutputPins: return None
        return self.__OutputStatus[pin]

    def set_output(self, pin, value, log_output = True):
        parsed_pin = doorpi.DoorPi().parse_string("!"+str(pin)+"!")
        if parsed_pin != "!"+str(pin)+"!":
            pin = parsed_pin

        pin = int(pin)
        value = str(value).lower() in ['1', 'high', 'on']
        log_output = str(log_output).lower() in ['true', 'log', '1', 'on']

        if not pin in self.__OutputPins: return False
        if log_output: logger.debug("out(pin = %s, value = %s, log_output = %s)", pin, value, log_output)

        RPiGPIO.output(pin, value)
        self.__OutputStatus[pin] = value
        return True

    get_input = status_inputpin
    get_output = status_output