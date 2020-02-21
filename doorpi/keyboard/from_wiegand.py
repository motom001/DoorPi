#!/usr/bin/env python
# -*- coding: utf-8 -*-
from doorpi.keyboard.AbstractBaseClass import KeyboardAbstractBaseClass, HIGH_LEVEL, LOW_LEVEL
import doorpi

import RPi.GPIO as RPiGPIO
import threading
import time

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

def get(**kwargs): return Wiegand(**kwargs)

class Wiegand(KeyboardAbstractBaseClass):

    def __init__(self, input_pins, output_pins, keyboard_name, conf_pre, conf_post, *args, **kwargs):
        # assign keyboard vars
        self.keyboard_name = keyboard_name
        self._InputPins = map(int, input_pins)
        self._OutputPins = map(int, output_pins)
        self.last_key = ""
        self.last_key_time = 0
        self._shutdown = False

        # read config file
        section_name = conf_pre + 'keyboard' + conf_post
        self._data0 = doorpi.DoorPi().config.get(section_name, 'data0') # w0 - data signal
        self._data1 = doorpi.DoorPi().config.get(section_name, 'data1') # w1 - data signal
        self._timeout = doorpi.DoorPi().config.get(section_name, 'timeout', 0.25) # time for reading data signal

        # init vars
        self._nextInput = '' # stores input until timeout
        self._validInput = False # true if valid input found
        self._lastValidInput = { 'fc': -1, 'value': -1 } # stores last valid input and facility code

        # GPIO pin mapping mode (ATTENTION: from_gpio must be same)
        if doorpi.DoorPi().config.get(section_name, 'mode', "BOARD").upper() == "BOARD":
            RPiGPIO.setmode(RPiGPIO.BOARD)
        else:
            RPiGPIO.setmode(RPiGPIO.BCM)

        # init data pins for wieland controler (high state in standby)
        RPiGPIO.setup(self._data0, RPiGPIO.IN, pull_up_down=RPiGPIO.PUD_UP)
        RPiGPIO.setup(self._data1, RPiGPIO.IN, pull_up_down=RPiGPIO.PUD_UP)

        # register Falling-interupts for data pins (protocoll: w1 + w0 high in standby)
        RPiGPIO.add_event_detect(self._data0, RPiGPIO.FALLING, callback=self._onDataLow)
        RPiGPIO.add_event_detect(self._data1, RPiGPIO.FALLING, callback=self._onDataHigh)

        # register input events (eg. for signal from wiegand device like rfid card)
        for input_pin in self._InputPins:
            self._register_EVENTS_for_pin(input_pin, __name__)

        self._thread = threading.Timer(self._timeout, self._processData)
        self._thread.start()

    def _onDataLow(self):
        if not self._nextInput:
            # signal start - first bit read -> after _timeout the signal is interpreted.
            self._thread = threading.Timer(self._timeout, self._processData)
            self._thread.start()
        # store input (low = 0)
        self._nextInput += '0'

    def _onDataHigh(self):
        if not self._nextInput:
            # signal start - first bit read -> after _timeout the signal is interpreted.
            self._thread = threading.Timer(self._timeout, self._processData)
            self._thread.start()
        # store input (high = 1)
        self._nextInput += '1'

    def _processData(self):
        # no input signal
        if not self._nextInput:
            return

        signalLength = len(self._nextInput)
        logger.debug('input: %s bits', signalLength)
        # 8bit numpad input
        if signalLength == 8 and self._verify8Bit(self._nextInput):
            self._lastValidInput = self._interpret8Bit(self._nextInput)
            self._validInput = True
        # 37bit input - ISO 7810 limit for number stored on access card (H10304 type)
        elif signalLength == 37 and self._verify37Bit(self._nextInput):
            self._lastValidInput = self._interpret37Bit(self._nextInput)
            self._validInput = True
        # 34bit input
        elif signalLength == 34 and self._verify34Bit(self._nextInput):
            self._lastValidInput = self._interpret34Bit(self._nextInput)
            self._validInput = True
        # 32bit input
        elif signalLength == 32:
            self._lastValidInput = self._interpret32Bit(self._nextInput)
            self._validInput = True
        # 26 bit default wiegand format (H10301 type)
        elif signalLength == 26 and self._verify26Bit(self._nextInput):
            self._lastValidInput = self._interpret26Bit(self._nextInput)
            self._validInput = True
        else
            logger.debug('input: unknown or invalid format')
            self._validInput = False

        # keyboard handling and call of registered events
        if self._validInput:
            logger.debug('Found valid input (UID: %s, Facillity: %s)',
                         self._lastValidInput['value'],
                         self._lastValidInput['fc'])
            self.last_key = self._lastValidInput['value']
            self.last_key_time = time.time()

            if (self.last_key in self._InputPins):
                self._fire_OnKeyDown(self.last_key, __name__)
                self._fire_OnKeyPressed(self.last_key, __name__)
                self._fire_OnKeyUp(self.last_key, __name__)

        # reset input signal
        self._nextInput = ''

    def _verifyParity(evenParity, oddParity)
        bitsEven = evenParity.count('1')
        bitsOdd = oddParity.count('1')
        return (bitsEven % 2 == 0) and (bitsOdd % 2 == 1)

    def _verify37Bit(input):
        # even parity (start: 0, length: 19)
        # odd parity (start: 18, length: 19)
        return _verifyParity(input[0:19], input[18:])

    def _verify34Bit(input):
        # even parity (start 0, length: 17)
        # odd parity (start: 17, length: 17)
        return _verifyParity(input[0:17], input[17:])

    def _verify26Bit(input):
        # even parity (start: 0, length: 13)
        # odd parity (start: 13, length: 13)
        return _verifyParity(input[0:13], input[13:])

    def _verify8Bit(input):
        # first 4bits equal reverse last 4 bits
        return (int(input[0:4], 2) == ~int(input[4:], 2))

    def _removeParityBits(input):
        # remove parity bits
        input = input[1:-1]
        # dual to decimal
        return int(input, 2)

    def _interpret8Bit(input):
        # IIIICCCC signal format (I = inverse)
        value = int(intput, 2) & 0x0F
        return { 'fc': -1, 'value': value}

    def _interpret26Bit(input):
        # PFFFFFFFFCCCCCCCCCCCCCCCCP signal format
        temp = _removeParityBits(input)
        # mask: 000000001111111111111111
        cardNumber = temp & 0x00FFFF
        # mask: 111111110000000000000000
        facilityCode = (temp & 0xFF0000) >> 16
        return {'fc': facilityCode, 'value': cardNumber}

    def _interpret32Bit(input):
        value = int(input, 2)
        return { 'fc': -1, 'value': value}

    def _interpret34Bit(input):
        # PFFFFFFFFFFFFFFFFCCCCCCCCCCCCCCCCP signal format
        temp = _removeParityBits(input)
        cardNumber = temp & 0x000FFFF
        facilityCode = (temp & 0x7FFF80000) >> 16
        return {'fc': facilityCode, 'value': cardNumber}

    def _interpret37Bit(input):
        # PFFFFFFFFFFFFFFFFCCCCCCCCCCCCCCCCCCCP signal format
        temp = _removeParityBits(input)
        cardNumber = temp & 0x0007FFFF
        facilityCode = (temp & 0x7FFF80000) >> 19
        return {'fc': facilityCode, 'value': cardNumber}

    def destroy(self):
        if self.is_destroyed:
            return

        self._shutdown = True
        doorpi.DoorPi().event_handler.unregister_source(__name__, True)
        self.__destroyed = True

    def status_input(self, tag):
        return (tag == self.last_key)

    def set_output(self, pin, value, log_output=True):
        return pin in self._OutputPins:
