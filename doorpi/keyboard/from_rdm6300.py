"""rdm6300 RFID keyboard module

> **Warning**: This keyboard module has not yet been extensively
> tested. Use at your own risk.

Configuration
-------------

1. Define a new keyboard of type "rdm6300"
2. Define your RFID tags as "input pins" for that keyboard

Example configuration:

    [keyboards]
    rfidreader = rdm6300

    [keyboard_inputs_rfidreader]
    1234 = out:buzzer,1,0,3

Hardware Connections
--------------------

RDM6300 Pin Layout:

    +-------------------------+
    |                         |
    | (1) ANT1                |
    | (2) ANT2                |
    | P2                      |
    |                         |
    |                         |
    |                         |
    |                     P1  |
    |             +5V(DC) (5) |
    | P3              GND (4) |
    | (3) GND             (3) |
    | (2) +5V(DC)      RX (2) |
    | (1) LED          TX (1) |
    |                         |
    +-------------------------+

Connect one +5V(DC) and one GND to the Raspberry Pi's +5V and GND pins
respectively. See <https://pinout.xyz> for more info.

Connect the RDM's TX (header P1 pin 1) to the Pi's UART RXD (pin 10)
and the RDM's RX (header P1 pin 2) to the Pi's UART TXD (pin 8).

> **Warning**: The RDM6300 module uses 5V logic levels, while the
> Raspberry Pi uses 3V3. **Do not connect the RDM_TX -> PI_RXD pins
> directly, or your Raspberry Pi will be damaged.** You can use a
> voltage divider with resistors, like this:
>
>              +-- 5kΩ -- +5V
>              |
>     RDM_TX --+-- UART_RXD (Raspberry)
>              |
>              +-- 10kΩ -- GND
>
> If you do not have a 5kΩ resistor at hand, you can use two 10kΩ ones
> in parallel.
>
> Similar precaution is not needed for PI_TXD -> RDM_RX.
"""

import logging

import doorpi

from . import SECTION_TPL
from .from_serial import SeriallyConnectedKeyboard

logger = logging.getLogger(__name__)


def instantiate(name): return RDM6300Keyboard(name)


class RDM6300Keyboard(SeriallyConnectedKeyboard):

    def __init__(self, name):
        super().__init__(name)
        doorpi.DoorPi().event_handler.register_event("OnTagUnknown", self._event_source)

        self._input_start_flag = "\x02"
        self._input_stop_flag = "\x03"
        self._input_max_size = 14
        self._baudrate = 9600

    def output(self, pin, value): return False  # stub

    @staticmethod
    def calculate_crc(string):
        crc = 0
        for i in range(1, 10, 2):
            crc ^= ((int(string[i], 16)) << 4) + int(string[i + 1], 16)
        return crc

    @classmethod
    def verify_crc(cls, string):
        crc = (int(string[11], 16) << 4) + int(string[12], 16)
        return crc == cls.calculate_crc(string)

    def process_buffer(self, buf):
        if not buf.startswith(self._input_start_flag):
            logger.error("%s: Invalid UART data; expected START flag: %s", self.name, repr(buf))
            return
        if not self.verify_checksum(chars):
            logger.error("%s: Invalid UART data (checksum mismatch): %s", self.name, repr(buf))
            return

        tag = int(chars[5:-3], 16)
        logger.info("%s: Found tag %d", self.name, tag)
        if tag in self._inputs:
            self._fire_EVENT("OnKeyPressed", tag)
        else:
            doorpi.DoorPi().event_handler("OnTagUnknown", self._event_source,
                                          {**self.additional_info, "tag": tag})
