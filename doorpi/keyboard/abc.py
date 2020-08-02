"""Abstract base class that helps implementing a keyboard module."""

import datetime
import logging

import doorpi
from doorpi import keyboard
from doorpi.actions import CallbackAction

from . import HIGH_LEVEL

LOGGER = logging.getLogger(__name__)


class AbstractKeyboard():
    """ABC that provides common functionality and helpers for keyboard modules."""

    def __init__(self, name, *, events=("OnKeyPressed", "OnKeyUp", "OnKeyDown")):
        """Common initialization.

        This should be called before keyboard-specific initialization
        is done in subclass __init__. It will set the following class
        members:

        * self.name = The name passed in
        * self.last_key = None; will hold the last triggered input
        * self.last_key_time = now; will hold the datetime when the
                               ``last_key`` was pressed
        * self.config = A ``ConfigView`` for the keyboard specific
                        configuration.
        * self._bouncetime = "bouncetime" in config
        * self._event_source = The "event source" name that is used to
                               associate events with this keyboard.
        * self._high_polarity = A boolean describing the configured
                                keyboard polarity (HIGH = True).
        * self._inputs = A list with all configured inputs
        * self._outputs = A dict with all configured outputs mapping to
                          their current states.
        * self._pressed_on_key_down = True if OnKeyPressed should be
              fired together with OnKeyDown, False for OnKeyUp. This is
              handled automatically by the helper functions
              `_fire_OnKeyDown` and `_fire_OnKeyUp`.

        Subclasses should also bring all pins to a known state at the
        end of their __init__. They need not go through `self.output()`
        but may use a more efficient method, since all pins are
        initialized as `False`. What `False` means depends on the value
        of `self._high_polarity`, so take care to `_normalize(False)`
        before actually passing it to the pin.

        Arguments:
        * `name`: The keyboard's name as passed in from the handler.
        * `events`: A tuple of event names that will be registered for
                    each configured input, in three forms:
                    1) the unmangled event name
                    2) EventName_InputName
                    3) EventName_KeyboardName.InputName
        """
        # pylint: disable=no-member  # Only available at runtime

        if not name:
            raise ValueError("Keyboard name must not be empty")

        self.name = name
        self.last_key = None
        self.last_key_time = datetime.datetime.now()
        LOGGER.debug("Creating %s", self)

        self.config = doorpi.INSTANCE.config.view(("keyboard", name))
        self._bouncetime = self.config["bouncetime"]
        self._event_source = f"keyboard.{self.__class__.__name__}.{name}"
        self._inputs = list(self.config.view("input"))
        self._outputs = dict.fromkeys(self.config.view("output"), False)
        self._pressed_on_key_down = self.config["pressed_on_key_down"]

        polarity = self.config["polarity"]
        self._high_polarity = polarity == keyboard.Polarity.HIGH

        eh = doorpi.INSTANCE.event_handler
        eh.register_source(self._event_source)
        for ev in events:
            eh.register_event(ev, self._event_source)
        for pin in self._inputs:
            for ev in events:
                eh.register_event(f"{ev}_{pin}", self._event_source)
                eh.register_event(f"{ev}_{self.name}.{pin}", self._event_source)

        eh.register_action("OnShutdown", CallbackAction(self.destroy))

    def destroy(self):
        self._deactivate()
        doorpi.INSTANCE.event_handler.unregister_source(self._event_source, force=True)

    def __str__(self):
        return f"{self.name} keyboard ({self.type})"

    def _deactivate(self):
        """Deactivate the keyboard in preparation for shutdown

        This will be called right before actually deleting the
        keyboard, and can be used e.g. to deactivate worker threads.
        """

    def input(self, pin):
        """Read an input pin

        This function returns the current value of the given input pin
        as bool. If the pin does not exist, it should return False.
        """
        if pin not in self._inputs:
            raise ValueError(f"Unknown input pin {self.name}.{pin}")
        return False

    def output(self, pin, value):
        """Set output pin ``pin`` to ``value``

        This function sets the given output pin to the given value. A
        keyboard implementation should normalize the passed value with
        ``self._normalize(value)`` to ensure it receives a bool.

        The implementation is required to update the ``self._outputs``
        dict if the actual pin state changed.

        Returns: True if the output pin was set or already had the
                 supplied value, False otherwise. This function should
                 not raise any Exceptions.
        See: ``_normalize()``
        """
        del value
        if pin not in self._outputs:
            raise ValueError(f"Unknown output pin {self.name}.{pin}")
        return False

    def self_check(self):
        """Check the correct functioning of this keyboard.

        This function will be periodically called to verify the
        keyboard is still functional. It should not return any value.
        In case the keyboard is found to be dysfunctional, it should
        raise an appropriate exception with a message describing what
        kind of problem was found.
        """

    # -----------------------------------------------------------------

    @property
    def type(self):
        """A human-readable keyboard type description."""
        return self.__class__.__name__

    @property
    def inputs(self):
        """The list of input pins that this keyboard uses."""
        return list(self._inputs)

    @property
    def outputs(self):
        """Maps this keyboard's output pins to their current states."""
        return dict(self._outputs)

    @property
    def additional_info(self):
        """A dict of information about this keyboard.

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
            "pin": self.last_key
        }

    @property
    def pressed_keys(self):
        """A list of currently pressed input pins."""
        return [p for p in self._inputs if self.input(p)]

    def _normalize(self, value):
        """Normalize the passed value to a bool.

        This function normalizes an arbitrary value to a bool. If the
        current keyboard's polarity is LOW, the value is also flipped.

        This helper should be called immediately after reading a value
        from an input pin, or immediately before writing the final
        value to an output pin.
        """

        if not isinstance(value, bool):
            value = str(value).strip().lower() in HIGH_LEVEL
        if not self._high_polarity: value = not value
        return value

    def _fire_event(self, event_name, pin):
        eh = doorpi.INSTANCE.event_handler
        doorpi.INSTANCE.keyboard.last_key = self.last_key = f"{self.name}.{pin}"

        extra = self.additional_info
        eh.fire_event(event_name, self._event_source, extra=extra)
        eh.fire_event(f"{event_name}_{pin}", self._event_source, extra=extra)
        eh.fire_event(f"{event_name}_{self.name}.{pin}", self._event_source, extra=extra)

    def _fire_keyup(self, pin):
        self._fire_event("OnKeyUp", pin)
        if not self._pressed_on_key_down: self._fire_event("OnKeyPressed", pin)

    def _fire_keydown(self, pin):
        self._fire_event("OnKeyDown", pin)
        if self._pressed_on_key_down: self._fire_event("OnKeyPressed", pin)
