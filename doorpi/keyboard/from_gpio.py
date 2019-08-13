import logging
import RPi.GPIO as gpio

import doorpi

from . import SECTION_TPL
from .abc import AbstractKeyboard

logger = logging.getLogger(__name__)
instantiated = False


def instantiate(name): return GPIOKeyboard(name)


class GPIOKeyboard(AbstractKeyboard):

    def __init__(self, name):
        global instantiated
        if instantiated: raise RuntimeError("Only one GPIO keyboard may be instantiated")
        instantiated = True

        super().__init__(name)

        gpio.setwarnings(False)

        conf = doorpi.DoorPi().config
        section_name = SECTION_TPL.format(name=name)
        mode = conf.get_string(section_name, "mode", "BOARD")
        if mode == "BOARD":
            gpio.setmode(gpio.BOARD)
        elif mode == "BCM":
            gpio.setmode(gpio.BCM)
        else:
            raise ValueError(f"{self.name}: Invalid address mode (must be BOARD or BCM)")

        pull = conf.get(section_name, "pull_up_down", "OFF")
        if pull == "OFF":
            pull = gpio.PUD_OFF
        elif pull == "UP":
            pull = gpio.PUD_UP
        elif pull == "DOWN":
            pull = gpio.PUD_DOWN
        else:
            raise ValueError(f"{self.name}: Invalid pull_up_down value (must be OFF, UP or DOWN)")

        gpio.setup(self._inputs, gpio.IN, pull_up_down=pull)
        for input_pin in self._inputs:
            gpio.add_event_detect(input_pin, gpio.BOTH, callback=self.event_detect,
                                  bouncetime=int(bouncetime))

        gpio.setup(self._outputs.keys(), gpio.OUT)
        for output_pin in self._outputs:
            self.output(output_pin, 0, False)

    def __del__(self):
        global instantiated

        for pin in self._outputs:
            self.output(pin, 0, False)
        gpio.cleanup()
        instantiated = False
        super().__del__()

    def event_detect(self, pin):
        if self.input(pin):
            self._fire_OnKeyDown(pin)
        else:
            self._fire_OnKeyUp(pin)

    def input(self, pin):
        pin = int(pin)
        if pin not in self._inputs: return False
        try:
            return self._normalize(gpio.input(pin))
        except Exception:
            logger.exception("%s: Error reading pin %s", self.name, pin)
            return False

    def output(self, pin, value):
        pin = int(pin)
        if pin not in self._outputs:
            return False

        value = self._normalize(value)
        logger.debug("%s: Setting GPIO pin %s to %s", self.name, pin, value)
        try:
            gpio.output(pin, value)
        except Exception:
            logger.exception("%s: Error trying to set pin %s to %s", self.name, pin, value)
            return False
        self._outputs[pin] = value
        return True
