"""Enumeration types used in the configuration file"""

import enum
import importlib.metadata

__all__ = [
    "GPIOMode",
    "GPIOPull",
    "KeyboardType",
    "Polarity",
]


KeyboardType = enum.Enum(  # type: ignore[misc]
    "KeyboardType",
    {i.name: i for i in importlib.metadata.entry_points()["doorpi.keyboards"]},
    module=__name__,
)


class GPIOMode(enum.Enum):
    """The pin numbering mode for the GPIOKeyboard"""

    BOARD = 1
    """Use numbers according to the header pinout (recommended)"""
    BCM = 2
    """Use numbers according to the internal chip wiring"""


class GPIOPull(enum.Enum):
    """Configure internal pull-up/down resistors"""

    OFF = enum.auto()
    """Do not use the internal pull-up/down resistors"""
    UP = enum.auto()
    """Use the internal pull-up resistors"""
    DOWN = enum.auto()
    """Use the internal pull-down resistors"""


class Polarity(enum.Enum):
    """Keyboard pin polarity"""

    HIGH = enum.auto()
    """VCC is True, GND is False"""
    LOW = enum.auto()
    """VCC is False, GND is True"""
