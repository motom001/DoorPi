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
import logging
import os
import serial
import threading
import time

import doorpi

from . import SECTION_TPL
from .abc import AbstractKeyboard

logger = logging.getLogger(__name__)


def instantiate(name): return SeriallyConnectedKeyboard(name)


class SeriallyConnectedKeyboard(AbstractKeyboard):

    def __init__(self, name, *, events=("OnKeyPressed",)):
        super().__init__(name, events=events)
        self.last_key_time = 0

        conf = doorpi.DoorPi().config
        section_name = SECTION_TPL.format(name=name)

        port = conf.get_string(section_name, "port", "")
        baudrate = conf.get_int(section_name, "baudrate", 9600)

        self._input_stop_flag = conf.get_string(section_name, "input_stop_flag", r"\n") \
                                    .replace(r"\n", "\n").encode("utf-8")
        self._input_max_size = conf.get_int(section_name, "input_max_size", 255)
        self._output_stop_flag = conf.get_string(section_name, "output_stop_flag", r"\n") \
                                     .replace(r"\n", "\n").encode("utf-8")

        if not port: raise ValueError(f"{self.name}: port must not be empty")
        if baudrate <= 0: raise ValueError(f"{self.name}: baudrate must be greater than 0")

        if not self._input_stop_flag:
            self._input_max_size = 1
        else:
            self._input_max_size += len(self._input_stop_flag)

        self._ser = serial.Serial(port, baudrate)

        self._ser.timeout = 1
        self._ser.open()

        self._shutdown = False
        self._exception = None
        self._thread = threading.Thread(target=self.read_usb_plain)
        self._thread.start()

    def _deactivate(self):
        self._shutdown = True
        if self._ser and self._ser.isOpen(): self._ser.close()
        self._thread.join()

    def input(self, pin): return False  # stub

    def output(self, pin, value):
        if pin not in self._outputs: return False
        value = self._normalize(value)

        if not self._ser or not self._ser.isOpen():
            logger.error("%s: Cannot write to keyboard: connection not open", self.name)
            return False

        if not value: return True

        try:
            self._ser.flushOutput()
            self._ser.write(pin)
            self._ser.write(self._output_stop_flag)
            self._ser.flush()
            return True
        except Exception:
            logger.exception("%s: Error writing to serial connection", self.name)
            return False

    def self_check(self):
        if self._exception is not None:
            raise RuntimeError(f"{self.name}: Worker died") from self._exception
        if not self._thread.is_alive():
            raise RuntimeError(f"{self.name}: Worker found dead without exception information")

    def read_serial(self):
        """Serial connection read function

        This function is run in a separate thread to listen for key
        presses sent by the keyboard.
        """

        buflen = self._input_max_size
        buf = collections.deque(maxlen=buflen + 1)  # + 1 to detect overflows
        stopflag = self._input_stop_flag
        try:
            while not self._shutdown:
                c = self._ser.read()
                logger.trace("%s: Read %s from serial connection", self.name, repr(c))
                if not c: continue
                buf += c
                # check STOP flag existence
                for i in range(-len(stopflag), 0):
                    if buf[i] != stopflag[i]: break
                else:  # STOP flag exists (or is empty)
                    now = time.time() * 1000
                    if len(buf) > buflen:  # buffer overrun
                        logger.warning("%s: Buffer overflow (> %d), discarding input",
                                       self.name, buflen)
                    elif now < self.last_key_time + self._bouncetime:
                        # debounce
                        pass
                    else:
                        self.last_key_time = now
                        # remove STOP flag
                        for i in range(len(stopflag)): buf.pop()
                        self.process_buffer(b"".join(buf))
                    buf.clear()
        except Exception as ex:
            if not self._shutdown:
                self._exception = ex

    def process_buffer(self, buf):
        """Process the buffer contents

        This function is called by the worker thread to process the
        buffer contents and fire the appropriate events after a STOP
        flag was received.

        The buffer is passed as undecoded bytes object. The passed
        buffer does not include the STOP flag.
        """

        for key in self._inputs:
            if buf == key:
                self._fire_EVENT("OnKeyPressed", buf)
                break
        else: logger.trace("%s: Ignoring unknown key %s", self.name, buf)