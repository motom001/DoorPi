"""Actions related to pin output: out"""
import threading
from typing import Any, Mapping

import doorpi

from . import Action, action


class OutAction(Action):
    """Sets a GPIO pin to a constant value."""

    def __init__(self, pin: str, value: str) -> None:
        super().__init__()
        self._pin = pin
        self._value = value

    def __call__(self, event_id: str, extra: Mapping[str, Any]) -> None:
        del event_id, extra
        self._setpin(self._value)

    def _setpin(self, value: str) -> None:
        if not doorpi.INSTANCE.keyboard.output(self._pin, value):
            raise RuntimeError(f"Cannot set pin {self._pin} to {value}")

    def __str__(self) -> str:
        return f"Set {self._pin} to {self._value}"

    def __repr__(self) -> str:
        return f"out:{self._pin},{self._value}"


class TriggeredOutAction(OutAction):
    """Holds a GPIO pin at a value for some time before setting it back."""

    def __init__(
        self,
        pin: str,
        startval: str,
        stopval: str,
        holdtime: str,
        intpin: str = None,
        /,
    ) -> None:
        super().__init__(pin, startval)
        self._stopval = stopval
        self._holdtime = float(holdtime)
        self._intpin = intpin
        self._int = threading.Event()
        if intpin:
            doorpi.INSTANCE.event_handler.register_action(
                f"OnKeyDown_{intpin}", self.interrupt
            )

    def __call__(self, event_id: str, extra: Mapping[str, Any]) -> None:
        self._setpin(self._value)
        self._int.clear()  # Make sure the flag is not set before waiting for it
        self._int.wait(timeout=self._holdtime)
        self._setpin(self._stopval)

    def interrupt(self, event_id: str, extra: Mapping[str, Any]) -> None:
        """Aborts the wait time, so that the pin will be reset immediately."""
        del event_id, extra
        self._int.set()

    def __str__(self) -> str:
        return (
            f"Hold {self._pin} at {self._value} for {self._holdtime}s"
            + f" or until {self._intpin} is pressed"
            if self._intpin
            else ""
        )

    def __repr__(self) -> str:
        return "".join(
            (
                "out:",
                ",".join(
                    (
                        self._pin,
                        self._value,
                        self._stopval,
                        str(self._holdtime),
                    )
                ),
                self._intpin or "",
            )
        )


@action("out")
def instantiate(*args: str) -> Action:
    """Create an ``out:`` action"""
    if len(args) <= 2:
        return OutAction(*args)
    return TriggeredOutAction(*args)
