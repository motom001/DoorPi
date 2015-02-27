#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#  Configuration
#  -------------
#
#  1. Define a new keyboard of type 'rdm6300'
#  2. Define inputPins section for that keyboard
#  3. Each RFID tag has a decimal number printed 
#     on the surface. This is the Input PIN number. 
#     Define this number and an appropriate action.
#
#  Sample:
#
#  [keyboards]
#  rfidreader = rdm6300
#  ...
#  [rfidreader_InputPins]
#  1234567 = out:Tueroeffner,1,0,3
#  2345678 = out:Tueroeffner,1,0,3
#
#  That's all...
#
#
#
#  Hardware Connections
#  --------------------
#
#  RDM6300 Pin Layout
#  +-------------------------+
#  |                         |
#  | (1) ANT1                |
#  | (2) ANT2                |
#  | P2                      |
#  |                         |
#  |                         |
#  |                         |
#  |                     P1  |
#  |             +5V(DC) (5) |
#  | P3              GND (4) |
#  | (3) GND             (3) |
#  | (2) +5V(DC)      RX (2) |
#  | (1) LED          TX (1) |
#  |                         |
#  +-------------------------+
#
#  Connect one of the two +5V(DC) and one of the two GND to 
#  5V (Pin 2 on the RaspberryPi Board) and to GND (Pin 6 on 
#  the RaspberryPi Board). As I used a ribbon cable, the 
#  simplest way was to connect to (4) and (5) of P1 from the RDM6300. 
# 
#  Then, connect TX (pin (1) of P1) to RXD from the UART (Pin 10 
#  on the RaspberryPi Board) - BUT NOT DIRECTLY, OTHERWISE YOU 
#  MIGHT DAMAGE YOUR RASPBERRY PI!!!
#  The RaspberryPi expects 3,3V level on the UART Pins, but the 
#  RDM6300 delivers 5V. 
#
#  Simplest solution for this is a voltage divider via resistors:
#     RDM6300 P1(1) <--- Resistor R1 ---> RasPi Board(Pin 10)
#     GND           <--- Resistor R2 ---> RasPi Board(Pin 10) 
#  Ideal solution: R1=5k, R2=10k, this will deliver exactly 3,3V 
#                  to RasPi Board(Pin 10)
#  Alternative solution: As most RaspberryPi bundles only contain 
#                        10k resistors, you might either use 2 
#                        10k resistors in parallel to get a 5k 
#                        resistor, or simply use 10k for R1 instead.
#                        R1=R2=10k will deliver 2,5V to RasPi 
#                        Board(Pin 10), but that works also.
#
#  Reference: I used this resource to learn how to work with RDM6300, 
#             how to connect it to the RaspberryPi and how to handle
#             RFID data: http://kampis-elektroecke.de/?page_id=3248
 
import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import threading
import serial 
import time

from keyboard.AbstractBaseClass import KeyboardAbstractBaseClass, HIGH_LEVEL, LOW_LEVEL
import doorpi

def get(**kwargs): return RDM6300(**kwargs)
class RDM6300(KeyboardAbstractBaseClass):
    name = 'RFID Reader RDM6300'

    def readUART(self):
        # initialize UART
        # make sure that terminal via UART is disabled
        # see http://kampis-elektroecke.de/?page_id=3248 for details
        self._UART = serial.Serial("/dev/ttyAMA0", 9600)
        self._UART.timeout = 1
        self._UART.close()
        self._UART.open()
        
        startFlagOccured = False
        chars = ""
        lastReadTag = 0
        lastReadTime = 0
        
        while(not(self._shutdown)):
            nextChar = self._UART.read() # blocks for max. 1 second
            if nextChar != "" and startFlagOccured:
                if nextChar == '\x03':
                    startFlagOccured = False
                    # check the data received
                    # first, check the length
                    logger.debug("checking the received message %s", chars)
                    if len(chars)!=12:
                        logger.debug("dismiss code, as length is not 12 chars")
                    else:
                        # calculate checksum
                        checkSum = 0;
                        for I in range(0, 9, 2):
                            checkSum = checkSum ^ ((int(chars[I], 16)) << 4) + int(chars[I+1], 16)
                        readCheckSum = (int(chars[10], 16) << 4) + int(chars[11], 16)
                        if checkSum != readCheckSum:
                            logger.debug("dismiss code, as calculated checksum %s is not identical to read checksum %s", checkSum, readCheckSum)
                        else:
                            # convert data to number
                            readTag = int(chars[4:10], 16)
                            ignoreThisTag = False
                            if lastReadTag==readTag:
                                now = time.time()
                                if (now-lastReadTime)<5:
                                    logger.debug("dismiss code, same tag within 5 seconds")
                                    ignoreThisTag = True
                            if not(ignoreThisTag):
                                logger.debug("valid RFID tag read '%s', firing events", readTag);
                                self._fire_OnKeyDown(readTag, __name__)
                                self._currentTag = readTag;
                                self._fire_OnKeyPressed(readTag, __name__)
                                time.sleep(3)
                                self._fire_OnKeyUp(readTag, __name__)
                                self._currentTag = 0;
                                lastReadTag = readTag
                                lastReadTime = time.time()
                    chars = ""                              
                else:
                    chars = chars + str(nextChar)
                    if len(chars)>12:
                        logger.debug("dismissing code %s, as length is greater than 12 chars", chars)
                        startFlagOccured = False
                        chars = ""
            elif nextChar == '\x02':
                startFlagOccured = True
                chars = ""

        # shutdown the UART
        self._UART.close();
        self._UART = None;
        logger.debug("readUART thread ended")
        
    def __init__(self, input_pins, keyboard_name, *args, **kwargs):
        logger.debug("__init__(input_pins = %s)", input_pins)
        self.keyboard_name = keyboard_name
        self._InputPins = map(int, input_pins)
        self._currentTag = 0;
        
        for input_pin in self._InputPins:
            self._register_EVENTS_for_pin(input_pin, __name__)


        self._shutdown = False
        self._thread = threading.Thread(target=self.readUART)
        self._thread.start()


    def destroy(self):
        logger.debug("destroy")
        self._shutdown = True
        doorpi.DoorPi().event_handler.unregister_source(__name__, True)

    def status_input(self, tag):
        logger.debug("status_input for tag %s", tag)
        if tag==self._currentTag:
            return True
        else:
            return False

    def set_output(self, pin, value, log_output = True):
        # RDM6300 does not support output
        return False
