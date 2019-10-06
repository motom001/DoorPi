import threading
from time import sleep

import doorpi
from . import Action


class OutAction(Action):
    def __init__(self, pin, value):
        self._pin = pin
        self._value = value

    def __call__(self, event_id, extra):
        self.setpin(self._value)

    def setpin(self, value):
        if not doorpi.DoorPi().keyboard.output(self._pin, value):
            raise RuntimeError(f"Cannot set pin {self._pin} to {value}")

    def __str__(self):
        return f"Set {self._pin} to {self._value}"

    def __repr__(self):
        return f"{__name__.split('.')[-1]}:{self._pin},{self._value}"


class TriggeredOutAction(OutAction):

    def __init__(self, pin, startval, stopval, holdtime, intpin=None):
        super().__init__(pin, startval)
        self._stopval = stopval
        self._holdtime = float(holdtime)
        self._intpin = intpin
        self._int = threading.Event()
        if intpin:
            doorpi.DoorPi().event_handler.register_action(f"OnKeyDown_{intpin}", self.interrupt)

    def __call__(self, event_id, extra):
        self.setpin(self._value)
        self._int.clear()  # Make sure the flag is not set before waiting for it
        self._int.wait(timeout=self._holdtime)
        self.setpin(self._stopval)

    def interrupt(self, event_id, extra):
        self._int.set()

    def __str__(self):
        return f"Hold {self._pin} at {self._value} for {self._holdtime}s" \
            + f" or until {self._intpin} is pressed" if self._intpin else ""

    def __repr__(self):
        return f"{__name__.split('.')[-1]}:{self._pin},{self._value},{self._stopval}," \
            f"{self._holdtime}{',' + self._intpin if self._intpin is not None else ''}"


def instantiate(*args):
    if len(args) <= 2:
        return OutAction(*args)
    else:
        return TriggeredOutAction(*args)
