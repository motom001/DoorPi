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
from typing import Any

import doorpi

from .from_serial import SeriallyConnectedKeyboard

LOGGER = logging.getLogger(__name__)


class RDM6300Keyboard(SeriallyConnectedKeyboard):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        doorpi.INSTANCE.event_handler.register_event(
            "OnTagUnknown", self._event_source
        )

        self._input_start_flag = b"\x02"
        self._input_stop_flag = b"\x03"
        self._input_max_size = 14
        self._baudrate = 9600

    def output(self, pin: str, value: Any) -> bool:
        del value  # stub
        raise ValueError(f"Unknown output pin {self.name}.{pin}")

    def process_buffer(self, buf: bytes) -> None:
        if not buf.startswith(self._input_start_flag):
            LOGGER.error(
                "%s: Invalid UART data; expected START flag: %r",
                self.name,
                buf,
            )
            return
        if not verify_crc(buf):
            LOGGER.error(
                "%s: Invalid UART data (checksum mismatch): %r", self.name, buf
            )
            return

        tag = int(buf[5:-3], 16)
        LOGGER.info("%s: Found tag %d", self.name, tag)
        if tag in self._inputs:
            self._fire_event("OnKeyPressed", str(tag))
        else:
            doorpi.INSTANCE.event_handler(
                "OnTagUnknown",
                self._event_source,
                extra={**self.additional_info, "tag": tag},
            )


def verify_crc(string: bytes) -> bool:
    """Verify the embedded checksum in the passed string"""
    crc = int(string[11:13], base=16)
    return crc == calculate_crc(string)


def calculate_crc(string: bytes) -> int:
    """Calculate the checksum of the passed string"""
    crc = 0
    for i in range(1, 10, 2):
        crc ^= int(string[i : i + 2], base=16)
    return crc


instantiate = RDM6300Keyboard  # pylint: disable=invalid-name
