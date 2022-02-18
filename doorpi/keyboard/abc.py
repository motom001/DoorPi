"""Abstract base class that helps implementing a keyboard module."""
import datetime
import logging
from typing import Any, Dict, Iterable, List, Optional

import doorpi
import doorpi.keyboard.enums
from doorpi import keyboard
from doorpi.actions import CallbackAction

from . import HIGH_LEVEL

LOGGER = logging.getLogger(__name__)


class AbstractKeyboard:
    """Common functionality and helpers for keyboard modules"""

    name: str
    "The configured name of this keyboard"
    last_key: Optional[str]
    "The last triggered input"
    last_key_time: datetime.datetime
    "The time when last_key was triggered"
    config: doorpi.config.ConfigView
    "View on this keyboard's configuration"

    _bouncetime: datetime.timedelta
    "The configured ``bouncetime``"
    _event_source: str
    """The "event source" name of this keyboard"""
    _high_polarity: bool
    "Configured keyboard polarity (True = HIGH)"
    _inputs: List[str]
    "All configured input pin names"
    _outputs: Dict[str, bool]
    "Configured output pins and their current states"
    _pressed_on_key_down: bool
    """Fire OnKeyPressed together with OnKeyDown (otherwise OnKeyUp)"""

    def __init__(
        self,
        name: str,
        *,
        events: Iterable[str] = ("OnKeyPressed", "OnKeyUp", "OnKeyDown"),
    ):
        """Common initialization

        This should be called before keyboard-specific initialization
        is done in subclass __init__. It will handle initialization of
        the attributes documented for this base class.

        Subclasses should also bring all pins to a known state at the
        end of their __init__. They need not go through `self.output()`
        but may use a more efficient method, since all pins are
        initialized as `False`. What `False` means depends on the value
        of `self._high_polarity`, so take care to `_normalize(False)`
        before actually passing it to the pin.

        Args:
            name: The keyboard's name as passed in from the handler.
            events: A tuple of event names that will be registered for
                each configured input, in three forms:

                1.  The unmangled event name
                2.  EventName_InputName
                3.  EventName_KeyboardName.InputName
        """
        if not name:
            raise ValueError("Keyboard name must not be empty")

        self.name = name
        self.last_key = None
        self.last_key_time = datetime.datetime.now()
        LOGGER.debug("Creating %s", self)

        self.config = doorpi.INSTANCE.config.view(("keyboard", name))
        self._bouncetime = datetime.timedelta(
            seconds=self.config["bouncetime"]
        )
        self._event_source = f"keyboard.{self.__class__.__name__}.{name}"
        self._inputs = list(self.config.view("input"))
        self._outputs = dict.fromkeys(self.config.view("output"), False)
        self._pressed_on_key_down = self.config["pressed_on_key_down"]

        polarity = self.config["polarity"]
        self._high_polarity = polarity is keyboard.enums.Polarity.HIGH

        eh = doorpi.INSTANCE.event_handler
        eh.register_source(self._event_source)
        for ev in events:
            eh.register_event(ev, self._event_source)
        for pin in self._inputs:
            for ev in events:
                eh.register_event(f"{ev}_{pin}", self._event_source)
                eh.register_event(
                    f"{ev}_{self.name}.{pin}", self._event_source
                )

        eh.register_action("OnShutdown", CallbackAction(self.destroy))

    def destroy(self) -> None:
        self._deactivate()
        doorpi.INSTANCE.event_handler.unregister_source(
            self._event_source, force=True
        )

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} keyboard ({self.type})"

    def _deactivate(self) -> None:
        """Deactivate the keyboard in preparation for shutdown

        This will be called right before actually deleting the
        keyboard, and can be used e.g. to deactivate worker threads.
        """

    def input(self, pin: str) -> bool:
        """Read an input pin

        This function returns the current value of the given input pin
        as bool. If the pin does not exist, it should return False.
        """
        if pin not in self._inputs:
            raise ValueError(f"Unknown input pin {self.name}.{pin}")
        return False

    def output(self, pin: str, value: Any) -> bool:
        """Set output pin ``pin`` to ``value``

        This function sets the given output pin to the given value. A
        keyboard implementation should normalize the passed value with
        ``self._normalize(value)`` to ensure it receives a bool.

        The implementation is required to update the ``self._outputs``
        dict if the actual pin state changed.

        Returns:
            True if the output pin was set or already had the supplied
            value, False otherwise
        Raises:
            ValueError: If the pin name is invalid
        See:
            ``_normalize()``
        """
        del value
        if pin not in self._outputs:
            raise ValueError(f"Unknown output pin {self.name}.{pin}")
        return False

    def self_check(self) -> None:
        """Check the correct functioning of this keyboard

        This function will be periodically called to verify the keyboard
        is still functional. It should not return any value.  In case
        the keyboard is found to be dysfunctional, it should raise an
        appropriate exception with a message describing the problem.
        """

    # -----------------------------------------------------------------

    @property
    def type(self) -> str:  # pragma: no cover
        """A human-readable keyboard type description"""
        return type(self).__name__

    @property
    def inputs(self) -> List[str]:  # pragma: no cover
        """The list of input pins that this keyboard uses"""
        return list(self._inputs)

    @property
    def outputs(self) -> Dict[str, bool]:  # pragma: no cover
        """Maps this keyboard's output pins to their current states"""
        return dict(self._outputs)

    @property
    def additional_info(self) -> Dict[str, Optional[str]]:  # pragma: no cover
        """A dict with information about this keyboard

        The dict available here provides the following information:

        * ``name``: The configuration name used by this instance.
        * ``type``: A human readable type for this keyboard.
        * ``pretty_name``: A human readable description for this instance.
        * ``pin``: The last pressed input pin.
        """
        return {
            "name": self.name,
            "type": self.type,
            "pretty_name": str(self),
            "pin": self.last_key,
        }

    @property
    def pressed_keys(self) -> List[str]:  # pragma: no cover
        """A list of currently pressed input pins"""
        return [p for p in self._inputs if self.input(p)]

    def _normalize(self, value: Any) -> bool:
        """Normalize the passed value to a bool

        This function normalizes an arbitrary value to a bool. If the
        current keyboard's polarity is LOW, the value is also flipped.

        This helper should be called immediately after reading a value
        from an input pin, or immediately before writing the final
        value to an output pin.
        """
        if not isinstance(value, bool):
            value = str(value).strip().lower() in HIGH_LEVEL
        if not self._high_polarity:
            value = not value
        return value

    def _fire_event(self, event_name: str, pin: str) -> None:
        eh = doorpi.INSTANCE.event_handler
        doorpi.INSTANCE.keyboard.last_key = (
            self.last_key
        ) = f"{self.name}.{pin}"

        extra = self.additional_info
        eh.fire_event(event_name, self._event_source, extra=extra)
        eh.fire_event(f"{event_name}_{pin}", self._event_source, extra=extra)
        eh.fire_event(
            f"{event_name}_{self.name}.{pin}", self._event_source, extra=extra
        )

    def _fire_keyup(self, pin: str) -> None:
        self._fire_event("OnKeyUp", pin)
        if not self._pressed_on_key_down:
            self._fire_event("OnKeyPressed", pin)

    def _fire_keydown(self, pin: str) -> None:
        self._fire_event("OnKeyDown", pin)
        if self._pressed_on_key_down:
            self._fire_event("OnKeyPressed", pin)
