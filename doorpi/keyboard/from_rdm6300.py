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
#  RFID data: http://kampis-elektroecke.de/?page_id=3248
import doorpi
from doorpi.keyboard.AbstractBaseClass import KeyboardAbstractBaseClass

import threading
import serial
import time

import logging
logger = logging.getLogger(__name__)
logger.debug('%s loaded', __name__)


def get(**kwargs): return RDM6300(**kwargs)


class RDM6300(KeyboardAbstractBaseClass):
    name = 'RFID Reader RDM6300'

    @staticmethod
    def calculate_checksum(string):
        checksum = 0
        for i in range(1, 10, 2):
            checksum ^= ((int(string[i], 16)) << 4) + int(string[i + 1], 16)
        return checksum

    @classmethod
    def verify_checksum(cls, buffer):
        # signal format: ttttiiiiiicc (t = tag, i = id, c = checksum) in hexa-system
        # -> compare to bit 11 + 12
        checksum = (int(buffer[11], 16) << 4) + int(buffer[12], 16)
        return (checksum == cls.calculate_checksum(buffer))

    def read_serial(self):
        while not self._shutdown:
            # initialize UART
            self._serial = serial.Serial(self.__port, self.__baudrate)
            self._serial.timeout = 1
            # make sure that terminal via UART is disabled
            self._serial.close()
            self._serial.open()

            try:
                buffer = ''

                while not self._shutdown:
                    # read next char from uart
                    input = self._serial.read()
                    if not input:
                        continue

                    # store input in buffer
                    buffer += str(input)

                    # check for end of signal flag
                    if (input == self._input_stop_flag):
                        # check signal format
                        if buffer.startswith(self._input_start_flag) and \
                           len(buffer) == self._input_frame_size and \
                           RDM6300.verify_checksum(buffer):
                            logger.debug('found tag, checking dismisstime')
                            # signal format ok - to fast?
                            now = time.time()
                            if (now - self.last_key_time) > self.__dismisstime:
                                # call Handler for unspecific found tag
                                doorpi.DoorPi().event_handler('OnFoundTag', __name__)
                                # signal format: ttttiiiiiicc (t = tag, i = id, c = checksum) in hexa-system
                                self.last_key = int(buffer[5:-3], 16)
                                self.last_key_time = now
                                logger.debug('id is %s', self.last_key)
                                # card uid registered as input pin?
                                if self.last_key in self._InputPins:
                                    # call events for uid und common event for known tags
                                    self._fire_OnKeyDown(
                                        self.last_key, __name__)
                                    self._fire_OnKeyPressed(
                                        self.last_key, __name__)
                                    self._fire_OnKeyUp(
                                        self.last_key, __name__)
                                    doorpi.DoorPi().event_handler('OnFoundKnownTag', __name__)
                                else:
                                    doorpi.DoorPi().event_handler('OnFoundUnknownTag', __name__)

                        # reset buffer after stop flag
                        buffer = ''
                    # signal to long? reset
                    elif len(buffer) > self._input_frame_size:
                        logger.debug('invalid signal length')
                        buffer = ''
            except Exception as ex:
                logger.exception(ex)
            finally:
                # shutdown the UART
                self._serial.close()
                self._serial = None

    def __init__(self, input_pins, keyboard_name, conf_pre, conf_post, *args, **kwargs):
        logger.debug('__init__ (input_pins = %s)', input_pins)
        self.keyboard_name = keyboard_name
        self._InputPins = list(map(int, input_pins))

        # register special events for cards (input pin signal is also valid!)
        doorpi.DoorPi().event_handler.register_event('OnFoundTag', __name__)
        doorpi.DoorPi().event_handler.register_event('OnFoundUnknownTag', __name__)
        doorpi.DoorPi().event_handler.register_event('OnFoundKnownTag', __name__)

        # init last card parameters
        self.last_key = ''
        self.last_key_time = 0

        # read settings from config
        section_name = conf_pre + 'keyboard' + conf_post
        self.__port = doorpi.DoorPi().config.get(section_name, 'port', '/dev/ttyAMA0')
        self.__baudrate = doorpi.DoorPi().config.get_int(section_name, 'baudrate', 9600)
        self.__dismisstime = doorpi.DoorPi().config.get_int(section_name, 'dismisstime', 5)
        self._input_start_flag = '\x02'
        self._input_stop_flag = '\x03'
        self._input_frame_size = 14

        # register events for uids specified in config
        for input_pin in self._InputPins:
            self._register_EVENTS_for_pin(input_pin, __name__)

        # call read function in thread to unblock main thread
        self._shutdown = False
        self._thread = threading.Thread(target=self.read_serial)
        self._thread.daemon = True
        self._thread.start()

        self.register_destroy_action()

    def destroy(self):
        if self.is_destroyed:
            return

        # stop reading process
        self._shutdown = True
        # unregister keyboard events
        doorpi.DoorPi().event_handler.unregister_source(__name__, True)
        self.__destroyed = True

    def status_input(self, tag):
        logger.debug('status_input for tag %s', tag)
        return (tag == self.last_key)

    def set_output(self, pin, value, log_output=True):
        # RDM6300 does not support output
        return False
