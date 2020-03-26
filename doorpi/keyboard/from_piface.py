"""PiFace keyboard module

> **Warning**: This keyboard module has not yet been extensively
> tested. Use at your own risk.

This keyboard module handles pins from the PiFace I/O Expander in
DoorPi.

Requirements:
- The `pifacedigitalio` python module.

> **Note**: Only one keyboard of type "piface" may be configured.
"""

import logging
import pifacedigitalio as piface  # pylint: disable=import-error

from .abc import AbstractKeyboard

LOGGER = logging.getLogger(__name__)
INSTANTIATED = False


class PifaceKeyboard(AbstractKeyboard):

    def __init__(self, name):
        global INSTANTIATED

        if INSTANTIATED: raise RuntimeError("Only one PiFace keyboard may be instantiated")
        INSTANTIATED = True

        super().__init__(name)

        piface.init()
        self.__listener = piface.InputEventListener()
        for input_pin in self._inputs:
            self.__listener.register(
                pin_num=input_pin,
                direction=piface.IODIR_BOTH,
                callback=self.event_detect,
                settle_time=self._bouncetime / 1000
            )
        self.__listener.activate()

    def __del__(self):
        global INSTANTIATED

        self.__listener.deactivate()
        for output_pin in self._outputs:
            self.output(output_pin, False)
        piface.deinit()
        INSTANTIATED = False
        super().__del__()

    def event_detect(self, event):
        if self.input(event.pin_num):
            self._fire_keydown(event.pin_num)
        else:
            self._fire_keyup(event.pin_num)

    def input(self, pin):
        super().input(pin)

        pin = int(pin)
        if pin not in self._inputs: return False
        return self._normalize(piface.digital_read(pin))

    def output(self, pin, value):
        super().output(pin, value)

        pin = int(pin)
        value = self._normalize(value)
        piface.digital_write(pin, value)
        self._outputs[pin] = value
        return True


instantiate = PifaceKeyboard  # pylint: disable=invalid-name
