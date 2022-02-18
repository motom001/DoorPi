"""The DoorPi keyboard modules

A keyboard module handles input from and output to specific hardware.
It is responsible for firing the appropriate events when buttons are
pressed, and to drive output pins as reaction to other events.

* `handler.py`: Contains the keyboard handler. It is responsible for
  translating pin aliases to physical pin names and directing input /
  output requests to the appropriate keyboard instance.
* `abc.py`: Contains an abstract base class with some helpful methods
  for implementing new keyboard modules.
* `from_*.py`: Contain the actual keyboard implementations.

The `*` in the keyboard module name is replaced by the "keyboard type",
which is used in the configuration file to select an implementation.

Each keyboard module must provide a top level function `instantiate()`,
which takes the configured keyboard name as sole argument and returns
a new instance of that keyboard module. The keyboard handler will
ensure that each name is unique.

Please refer to the `AbstractKeyboard` class in `abc.py` to learn more
about the methods and fields that a keyboard module should provide.

The following events are defined for keyboard modules:

- `OnKeyDown`, `OnKeyDown_[pinname]`, `OnKeyDown_[keyboard].[pinname]`

  These events are fired when a key changes state from "not pressed"
  to "pressed".
- `OnKeyUp` and the above variants

  These events are fired when a key changes state from "pressed" to
  "not pressed".
- `OnKeyPressed` and the above variants

  The pressed events are fired along with either "OnKeyDown" or
  "OnKeyUp", depending on the configuration key "pressed_on_key_down".

  If a keyboard does not have a notion of keys that are pressed or not
  pressed, it should **only** fire the pressed event. The RFID and NFC
  reader implementation fire "OnKeyPressed" events when a configured
  tag is detected.
- `OnTagUnknown` (no variants)
  This event is fired by the RFID and NFC reader implementation when a
  tag that was not registered was detected. The tag's ID is supplied in
  the event's extra information as `tag`.
"""
from __future__ import annotations

import doorpi

HIGH_LEVEL = frozenset({"1", "high", "on", "true"})


def load() -> doorpi.keyboard.handler.KeyboardHandler:
    """Loads the keyboard handler."""
    from . import handler  # pylint: disable=import-outside-toplevel

    return handler.KeyboardHandler()
