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
from typing import Any, Literal

import pifacecommon
import pifacedigitalio

from .abc import AbstractKeyboard

LOGGER = logging.getLogger(__name__)
INSTANTIATED = False


class PifaceKeyboard(AbstractKeyboard):
    def __init__(self, name: str) -> None:
        global INSTANTIATED

        if INSTANTIATED:
            raise RuntimeError("Only one PiFace keyboard may be instantiated")
        INSTANTIATED = True

        super().__init__(name)

        pifacedigitalio.init()
        self.__listener = pifacedigitalio.InputEventListener()
        for input_pin in self._inputs:
            self.__listener.register(
                pin_num=input_pin,
                direction=pifacedigitalio.IODIR_BOTH,
                callback=self.event_detect,
                settle_time=self._bouncetime / 1000,
            )
        self.__listener.activate()

    def destroy(self) -> None:
        global INSTANTIATED

        self.__listener.deactivate()
        for output_pin in self._outputs:
            self.output(output_pin, False)
        pifacedigitalio.deinit()
        INSTANTIATED = False
        super().destroy()

    def event_detect(self, event: pifacecommon.InterruptEvent) -> None:
        """Callback from PifaceDigitalIO library"""
        if self.input(event.pin_num):
            self._fire_keydown(event.pin_num)
        else:
            self._fire_keyup(event.pin_num)

    def input(self, pin: str) -> bool:
        super().input(pin)
        return self._normalize(pifacedigitalio.digital_read(int(pin)))

    def output(self, pin: str, value: Any) -> Literal[True]:
        super().output(pin, value)

        value = self._normalize(value)
        pifacedigitalio.digital_write(int(pin), value)
        self._outputs[pin] = value
        return True
