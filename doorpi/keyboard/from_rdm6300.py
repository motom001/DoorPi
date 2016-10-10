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

from doorpi.keyboard.AbstractBaseClass import KeyboardAbstractBaseClass, HIGH_LEVEL, LOW_LEVEL
import doorpi

START_FLAG = '\x02'
STOP_FLAG = '\x03'
MAX_LENGTH = 14

def get(**kwargs): return RDM6300(**kwargs)
class RDM6300(KeyboardAbstractBaseClass):
    name = 'RFID Reader RDM6300'

    @staticmethod
    def calculate_checksum(string):
        checkSum = 0
        for I in range(1, 10, 2):
            checkSum = checkSum ^ ((int(string[I], 16)) << 4) + int(string[I+1], 16)
        return checkSum

    @staticmethod
    def check_checksum(string):
        given_checksum = (int(string[11], 16) << 4) + int(string[12], 16)
        return given_checksum == RDM6300.calculate_checksum(string)

    def readUART(self):
        while not self._shutdown:
            logger.debug("readUART() started")
            # initialize UART
            # make sure that terminal via UART is disabled
            # see http://kampis-elektroecke.de/?page_id=3248 for details
            self._UART = serial.Serial(self.__port, self.__baudrate)
            self._UART.timeout = 1
            self._UART.close()
            self._UART.open()
            try:
                chars = ""

                while not self._shutdown:
                    # char aus buffer holen
                    newChar = self._UART.read()
                    if newChar != "":
                        logger.debug("new char %s read", newChar)
                        chars += str(newChar)

                        # aktuelles Ergebnis kontrollieren
                        if newChar == STOP_FLAG and chars[0] == START_FLAG and len(chars) == MAX_LENGTH and RDM6300.check_checksum(chars):
                            logger.debug("found tag, checking dismisstime")
                            # alles okay... nur noch schauen, ob das nicht eine Erkennungs-Wiederholung ist
                            now = time.time()
                            if now - self.last_key_time > self.__dismisstime:
                                doorpi.DoorPi().event_handler('OnFoundTag', __name__)
                                self.last_key = int(chars[5:-3], 16)
                                self.last_key_time = now
                                logger.debug("key is %s", self.last_key)
                                if self.last_key in self._InputPins:
                                    self._fire_OnKeyDown(self.last_key, __name__)
                                    self._fire_OnKeyPressed(self.last_key, __name__)
                                    self._fire_OnKeyUp(self.last_key, __name__)
                                    doorpi.DoorPi().event_handler('OnFoundKnownTag', __name__)
                                else:
                                    doorpi.DoorPi().event_handler('OnFoundUnknownTag', __name__)

                        # ggf. löschen
                        if newChar == STOP_FLAG or len(chars) > MAX_LENGTH:
                            chars = ""

            except Exception as ex:
                logger.exception(ex)
            finally:
                # shutdown the UART
                self._UART.close()
                self._UART = None
                logger.debug("readUART thread ended")

        
    def __init__(self, input_pins, keyboard_name, conf_pre, conf_post, *args, **kwargs):
        logger.debug("__init__ (input_pins = %s)", input_pins)
        self.keyboard_name = keyboard_name
        self._InputPins = map(int, input_pins)

        doorpi.DoorPi().event_handler.register_event('OnFoundTag', __name__)
        doorpi.DoorPi().event_handler.register_event('OnFoundUnknownTag', __name__)
        doorpi.DoorPi().event_handler.register_event('OnFoundKnownTag', __name__)

        self.last_key = ""
        self.last_key_time = 0

        # somit wirds aus der Config-Datei geladen, falls dort vorhanden.
        section_name = conf_pre+'keyboard'+conf_post
        self.__port = doorpi.DoorPi().config.get(section_name, 'port', "/dev/ttyAMA0")
        self.__baudrate = doorpi.DoorPi().config.get_int(section_name, 'baudrate', 9600)
        self.__dismisstime = doorpi.DoorPi().config.get_int(section_name, 'dismisstime', 5)

        for input_pin in self._InputPins:
            self._register_EVENTS_for_pin(input_pin, __name__)

        self._shutdown = False
        self._thread = threading.Thread(target = self.readUART)
        self._thread.daemon = True
        self._thread.start()

        self.register_destroy_action()

    def destroy(self):
        if self.is_destroyed: return
        logger.debug("destroy")
        self._shutdown = True
        doorpi.DoorPi().event_handler.unregister_source(__name__, True)
        self.__destroyed = True

    def status_input(self, tag):
        logger.debug("status_input for tag %s", tag)
        if tag == self.last_key:
            return True
        else:
            return False

    def set_output(self, pin, value, log_output = True):
        # RDM6300 does not support output
        return False
