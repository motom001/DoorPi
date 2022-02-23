#!/usr/bin/env python
# -*- coding: utf-8 -*-
from doorpi.keyboard.AbstractBaseClass import KeyboardAbstractBaseClass, HIGH_LEVEL, LOW_LEVEL
import doorpi

import threading
import serial
import time
from os import linesep as OS_LINESEP

import logging
logger = logging.getLogger(__name__)
logger.debug('%s loaded', __name__)

CONFIG = doorpi.DoorPi().config


def get(**kwargs): return UsbPlain(**kwargs)


class UsbPlain(KeyboardAbstractBaseClass):
    name = 'UsbPlain Keyboard'

    @property
    def last_received_chars(self): return self._last_received_chars

    _ser = None

    def read_usb_plain(self):
        self._last_received_chars = ''
        while not self._shutdown and self._ser.isOpen():
            # read next byte
            input = self._ser.read()
            if not input:
                continue

            self._last_received_chars += str(input)
            logger.debug('new char %s read and is now %s',
                         input, self._last_received_chars)

            # check wether input is registered as input-pin and take action
            for input_pin in self._InputPins:
                if self._last_received_chars.endswith(input_pin):
                    self.last_key = input_pin
                    self._fire_OnKeyDown(input_pin, __name__)
                    self._fire_OnKeyPressed(input_pin, __name__)
                    self._fire_OnKeyUp(input_pin, __name__)

            # check for stop/reset flag
            if self._last_received_chars.endswith(self._input_stop_flag):
                logger.debug('found input stop flag -> clear received chars')
                self._last_received_chars = ''
            # check for max. input length
            elif len(self._last_received_chars) > self._input_max_size:
                logger.debug(
                    'signal length bigger then max size -> clear received chars')
                self._last_received_chars = ''

    def __init__(self, input_pins, output_pins, conf_pre, conf_post, keyboard_name, *args, **kwargs):
        logger.debug(
            'FileSystem.__init__(input_pins = %s, output_pins = %s)', input_pins, output_pins)
        self.keyboard_name = keyboard_name
        self._InputPins = list(map(str, input_pins))
        self._OutputPins = list(map(str, output_pins))

        self._last_received_chars = ''
        self.last_key = ''

        # register events for all given input pins
        for input_pin in self._InputPins:
            self._register_EVENTS_for_pin(input_pin, __name__)

        # use set_output to register status @ dict self.__OutputStatus
        for output_pin in self._OutputPins:
            self.set_output(output_pin, 0, False)

        section_name = conf_pre + 'keyboard' + conf_post

        # read doorpi-config/settings for filesystem keyboard
        self._port = doorpi.DoorPi().config.get(section_name, 'port', '/dev/ttyUSB0')
        self._baudrate = doorpi.DoorPi().config.get_int(section_name, 'baudrate', 9600)
        self._input_stop_flag = doorpi.DoorPi().config.get(
            section_name, 'input_stop_flag', OS_LINESEP)
        self._input_max_size = doorpi.DoorPi().config.get_int(
            section_name, 'input_max_size', 255)
        self._output_stop_flag = doorpi.DoorPi().config.get(
            section_name, 'output_stop_flag', OS_LINESEP)

        # open serial connection
        self._ser = serial.Serial(self._port, self._baudrate)
        self._ser.timeout = 1  # block read, 0 for #non-block read, > 0 for timeout block read
        self._ser.close()
        self._ser.open()

        # start reading in seperat thread to unblock main thread
        self._shutdown = False
        self._thread = threading.Thread(target=self.read_usb_plain)
        self._thread.daemon = True
        self._thread.start()

        # register event for safe destroy (destroy-func)
        self.register_destroy_action()

    def destroy(self):
        if self.is_destroyed:
            return

        # close reading thread
        self._shutdown = True
        # clean serial connection
        if self._ser and self._ser.isOpen():
            self._ser.close()
        # unregister all doorpi events for this keyboard
        doorpi.DoorPi().event_handler.unregister_source(__name__, True)
        self.__destroyed = True

    def status_input(self, input_pin):
        logger.debug('status_input for tag %s', input_pin)
        return (input_pin == self.last_key)

    def set_output(self, pin, value, log_output=True):
        # check connection
        if not self._ser or not self._ser.isOpen():
            if log_output:
                logger.warning('serial write error: connection not open')
            return False

        if log_output:
            logger.debug('try to write %s to serial usb plain', pin)
        # write output to serial (with stop flag). output is pin
        self._ser.flushOutput()
        self._ser.write(pin + self._output_stop_flag)
        self._ser.flush()
        return True
