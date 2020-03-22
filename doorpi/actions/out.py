"""Actions related to pin output: out"""

import threading

import doorpi
from . import action


class OutAction:
    """Sets a GPIO pin to a constant value."""

    def __init__(self, pin, value):
        self._pin = pin
        self._value = value

    def __call__(self, event_id, extra):
        self._setpin(self._value)

    def _setpin(self, value):
        if not doorpi.DoorPi().keyboard.output(self._pin, value):
            raise RuntimeError(f"Cannot set pin {self._pin} to {value}")

    def __str__(self):
        return f"Set {self._pin} to {self._value}"

    def __repr__(self):
        return f"out:{self._pin},{self._value}"


class TriggeredOutAction(OutAction):
    """Holds a GPIO pin at a value for some time before setting it back."""

    def __init__(self, pin, startval, stopval, holdtime, intpin=None):
        super().__init__(pin, startval)
        self._stopval = stopval
        self._holdtime = float(holdtime)
        self._intpin = intpin
        self._int = threading.Event()
        if intpin:
            doorpi.DoorPi().event_handler.register_action(f"OnKeyDown_{intpin}", self.interrupt)

    def __call__(self, event_id, extra):
        self._setpin(self._value)
        self._int.clear()  # Make sure the flag is not set before waiting for it
        self._int.wait(timeout=self._holdtime)
        self._setpin(self._stopval)

    def interrupt(self, event_id, extra):
        """Aborts the wait time, so that the pin will be reset immediately."""
        del event_id, extra
        self._int.set()

    def __str__(self):
        return f"Hold {self._pin} at {self._value} for {self._holdtime}s" \
            + f" or until {self._intpin} is pressed" if self._intpin else ""

    def __repr__(self):
        return f"out:{self._pin},{self._value},{self._stopval}," \
            f"{self._holdtime}{',' + self._intpin if self._intpin is not None else ''}"


@action("out")
def instantiate(*args):
    if len(args) <= 2:
        return OutAction(*args)
    return TriggeredOutAction(*args)
