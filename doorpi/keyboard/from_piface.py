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
import pifacedigitalio as piface

import doorpi
from .abc import AbstractKeyboard

logger = logging.getLogger(__name__)
instantiated = False


def instantiate(name): return PifaceKeyboard(name)


class PifaceKeyboard(AbstractKeyboard):

    def __init__(self, name):
        global instantiated

        if instantiated: raise RuntimeError("Only one PiFace keyboard may be instantiated")
        instantiated = True

        super().__init__(name)

        piface.init()
        self.__listener = piface.InputEventListener()
        for input_pin in self._inputs:
            self.__listener.register(
                pin_num=input_pin,
                direction=piface.IODIR_BOTH,
                callback=self.event_detect,
                settle_time=bouncetime / 1000
            )
        self.__listener.activate()

    def __del__(self):
        global instantiated

        self.__listener.deactivate()
        for output_pin in self._outputs:
            self.output(output_pin, 0, False)
        piface.deinit()
        instantiated = False
        super().__del__()

    def event_detect(self, event):
        if self.input(event.pin_num):
            self._fire_OnKeyDown(event.pin_num)
        else:
            self._fire_OnKeyUp(event.pin_num)

    def input(self, pin):
        pin = int(pin)
        if pin not in self._inputs: return False
        return self._normalize(piface.digital_read(pin))

    def output(self, pin, value):
        pin = int(pin)
        if pin not in self._outputs: return False

        value = self._normalize(value)
        logger.debug("%s: Setting Piface pin %s to %s", self.name, pin, value)

        try: piface.digital_write(pin, value)
        except Exception:
            logger.exception("%s: Error setting Piface pin %s to %s", self.name, pin, value)
            return False

        self._outputs[pin] = value
        return True
