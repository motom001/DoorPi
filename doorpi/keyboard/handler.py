"""This module houses the keyboard handler."""
import importlib
import logging

import doorpi
from doorpi.actions import CheckAction

from . import SECTION_KEYBOARDS, SECTION_TPL_IN, SECTION_TPL_OUT

LOGGER = logging.getLogger(__name__)


class KeyboardHandler:
    """The keyboard handler.

    This class is responsible for constructing the individual keyboard
    instances, dispatching output events to and querying inputs from them.
    """

    def __init__(self):
        self.last_key = None

        self.__aliases = {}
        self.__keyboards = {}

        eh = doorpi.DoorPi().event_handler
        conf = doorpi.DoorPi().config
        kbnames = conf.get_keys(SECTION_KEYBOARDS)
        LOGGER.info("Instantiating %d keyboard(s): %s", len(kbnames), ", ".join(kbnames))

        for kbname in kbnames:
            if kbname in self.__keyboards: raise ValueError(f"Duplicate keyboard name {kbname}")
            kbtype = conf.get_string(SECTION_KEYBOARDS, kbname)
            LOGGER.debug("Instantiating keyboard %r (from_%s)", kbname, kbtype)

            kb = importlib.import_module(f"doorpi.keyboard.from_{kbtype}").instantiate(kbname)
            self.__keyboards[kbname] = kb

            # register input pin actions
            LOGGER.debug("Registering input pins for %r", kbname)
            section = SECTION_TPL_IN.format(name=kbname)
            pins = conf.get_keys(section)
            for pin in pins:
                action = conf.get_string(section, pin)
                if action:
                    eh.register_action(f"OnKeyPressed_{kbname}.{pin}", action)

            # register output pin aliases
            LOGGER.debug("Registering output pins for %r", kbname)
            section = SECTION_TPL_OUT.format(name=kbname)
            pins = conf.get_keys(section)
            self.__aliases[kbname] = {}
            for pin in pins:
                alias = conf.get_string(section, pin)
                if not alias: alias = pin
                if alias in self.__aliases[kbname]:
                    raise ValueError(f"Duplicate pin alias {kbname}.{alias}")
                self.__aliases[kbname].update({alias: pin})

        eh.register_action("OnTimeTick", CheckAction(self.self_check))

    def input(self, pinpath):
        """Polls an input for its current value."""
        try:
            kb, _, pin = self._decode_pinpath(pinpath)
        except ValueError:
            LOGGER.exception("Malformed pin: %s", pinpath)
            return False

        try:
            return kb.input(pin)
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("Error reading from pin %s", pinpath)
        return False

    def output(self, pinpath, value):
        """Sets an output pin to a value."""
        try:
            kb, kbname, pinalias = self._decode_pinpath(pinpath)
            pin = self.__aliases[kbname][pinalias]
            return kb.output(pin, value)
        except KeyError:
            LOGGER.exception("Unknown keyboard or pin: %s", pinpath)
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("Cannot output to pin %s", pinpath)
        return False

    def self_check(self):
        """Checks integrity of this handler and all attached keyboards.

        If a keyboard fails its self check, it will be logged and the
        program will be terminated.
        """
        abort = False
        for kbname, kb in self.__keyboards.items():
            try:
                kb.self_check()
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception("Keyboard %s failed self check", kbname)
                abort = True
        if abort:
            doorpi.DoorPi().doorpi_shutdown()

    def enumerate_outputs(self):
        """Enumerates all known output pins."""
        pins = {}
        for kbname, kbaliases in self.__aliases.items():
            pins.update({alias: f"{kbname}.{pin}" for alias, pin in kbaliases.items()})
        return pins

    def _decode_pinpath(self, pinpath):
        try:
            kbname, pin = pinpath.split(".")
        except ValueError:
            raise ValueError(f"Cannot decode pin name {pinpath!r}") from None

        if not kbname:
            raise ValueError(f"Empty keyboard name given ({pinpath!r}")
        if not pin:
            raise ValueError(f"Empty pin alias given ({pinpath!r})")

        kb = self.__keyboards.get(kbname)
        if kb is None:
            raise ValueError(f"Unknown keyboard name {kbname!r}")

        return kb, kbname, pin
