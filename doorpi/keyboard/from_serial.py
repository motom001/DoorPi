r"""The serial keyboard module.

> **Warning**: This keyboard module has not yet been extensively
> tested. Use at your own risk.

Requirements
************

This keyboard module can be used with any keyboard that is recognized
as serial connection, and that sends simple commands of the form:

    <seq><EOL>

where <seq> is a character sequence identifying the pressed key, and
<EOL> is an arbitrary terminator (e.g. the newline character). If it
supports output, it will accept commands in the same format.

Other keyboard modules are also available which communicate with
specific serially connected hardware, for example the RDM6300 RFID
reader. These usually require less setup and are easier to use.

Configuration
*************

In the `[keyboards]` section, add a keyboard of type `usb_plain`. In
its keyboard specific configuration section, make sure that the
following settings match what the keyboard hardware expects:

    # The serial port used to communicate. Must be set manually.
    port =
    # The baud rate (connection speed)
    baudrate = 9600
    # The character terminating a key sequence
    input_stop_flag = \n
    # The maximum buffer size for key sequences. A stop flag is
    # expected within this many received characters, or the input
    # is discarded as invalid.
    input_max_size = 255
    # The character used to terminate an output command
    output_stop_flag = \n

In `input_stop_flag` and `output_stop_flag`, the following character
sequence is replaced before processing begins:

    \n => (newline character)

Other configuration options not mentioned here are ignored.

If the keyboard hardware does not send a special stop flag, leave the
"input_stop_flag" option empty. In that case, each character sent over
the wire will be handled separately.
"""
import collections
import datetime
import logging
import threading
from typing import Any, Deque, Iterable, Optional

import serial  # pylint: disable=import-error

import doorpi

from .abc import AbstractKeyboard

LOGGER: doorpi.DoorPiLogger = logging.getLogger(__name__)  # type: ignore


class SeriallyConnectedKeyboard(AbstractKeyboard):
    def __init__(
        self,
        name: str,
        *,
        events: Iterable[str] = ("OnKeyPressed",),
    ) -> None:
        super().__init__(name, events=events)

        port = self.config["port"]
        baudrate = self.config["baudrate"]

        self._input_max_size = self.config["input_buffer_size"]
        self._input_stop_flag = self.config["input_stop_flag"].encode("utf-8")
        self._output_stop_flag = self.config["output_stop_flag"].encode(
            "utf-8"
        )

        if not port:
            raise ValueError(f"{self.name}: port must not be empty")
        if baudrate <= 0:
            raise ValueError(f"{self.name}: baudrate must be greater than 0")

        if not self._input_stop_flag:
            self._input_max_size = 1
        else:
            self._input_max_size += len(self._input_stop_flag)

        self._ser = serial.Serial(port, baudrate)

        self._ser.timeout = 1
        self._ser.open()

        self._shutdown = False
        self._exception: Optional[Exception] = None
        self._thread = threading.Thread(target=self.read_serial)
        self._thread.start()

    def _deactivate(self) -> None:
        self._shutdown = True
        if self._ser and self._ser.isOpen():
            self._ser.close()
        self._thread.join()

    def output(self, pin: str, value: Any) -> bool:
        super().output(pin, value)
        value = self._normalize(value)

        if not self._ser or not self._ser.isOpen():
            LOGGER.error(
                "%s: Cannot write to keyboard: connection not open", self.name
            )
            return False

        if not value:
            return True

        self._ser.flushOutput()
        self._ser.write(pin)
        self._ser.write(self._output_stop_flag)
        self._ser.flush()
        return True

    def self_check(self) -> None:
        if self._exception is not None:
            raise RuntimeError(
                f"{self.name}: Worker died"
            ) from self._exception
        if not self._thread.is_alive():
            raise RuntimeError(
                f"{self.name}: Worker found dead without exception information"
            )

    def read_serial(self) -> None:
        """Serial connection read function

        This function is run in a separate thread to listen for key
        presses sent by the keyboard.
        """

        buflen = self._input_max_size
        buf: Deque[bytes] = collections.deque(maxlen=buflen + 1)
        stopflag = self._input_stop_flag
        try:
            while not self._shutdown:
                chars = self._ser.read()
                LOGGER.trace(
                    "%s: Read %r from serial connection", self.name, chars
                )
                if not chars:
                    continue
                buf += chars
                # check STOP flag existence
                for i in range(-len(stopflag), 0):
                    if buf[i] != stopflag[i]:
                        break
                else:  # STOP flag exists (or is empty)
                    now = datetime.datetime.now()
                    if len(buf) > buflen:  # buffer overrun
                        LOGGER.warning(
                            "%s: Buffer overflow (> %d), discarding input",
                            self.name,
                            buflen,
                        )
                    elif now < self.last_key_time + self._bouncetime:
                        # debounce
                        pass
                    else:
                        self.last_key_time = now
                        # remove STOP flag
                        for i in range(len(stopflag)):
                            buf.pop()
                        self.process_buffer(b"".join(buf))
                    buf.clear()
        except Exception as ex:  # pylint: disable=broad-except
            if not self._shutdown:
                self._exception = ex

    def process_buffer(self, buf: bytes) -> None:
        """Process the buffer contents

        This function is called by the worker thread to process the
        buffer contents and fire the appropriate events after a STOP
        flag was received.

        The buffer is passed as undecoded bytes object. The passed
        buffer does not include the STOP flag.
        """
        decbuf = buf.decode("utf-8")
        for key in self._inputs:
            if decbuf == key:
                self._fire_event("OnKeyPressed", decbuf)
                break
        else:
            LOGGER.trace("%s: Ignoring unknown key %s", self.name, decbuf)


instantiate = SeriallyConnectedKeyboard  # pylint: disable=invalid-name
