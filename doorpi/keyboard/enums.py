"""Enumeration types used in the configuration file"""

import enum

__all__ = [
    "GPIOMode",
    "GPIOPull",
    "KeyboardType",
    "Polarity",
]


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


class KeyboardType(enum.Enum):
    """The type of keyboard"""

    filesystem = enum.auto()
    """Pseudo-keyboard using files (requires ``watchdog``)"""
    gpio = enum.auto()
    """Raspberry Pi onboard header (requires ``RPi.GPIO``)"""
    piface = enum.auto()
    """PiFace IO expander (requires ``piface``)"""
    pn532 = enum.auto()
    """PN532 NFC module (requires ``nfc``)"""
    rdm6300 = enum.auto()
    """RDM6300 RFID module (requires ``serial``)"""
    serial = enum.auto()
    """Serially connected keyboard (requires ``serial``)"""


class Polarity(enum.Enum):
    """Keyboard pin polarity"""

    HIGH = enum.auto()
    """VCC is True, GND is False"""
    LOW = enum.auto()
    """VCC is False, GND is True"""
