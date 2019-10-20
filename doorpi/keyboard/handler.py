import importlib
import logging

import doorpi
from doorpi.actions import CallbackAction

from . import SECTION_KEYBOARDS, SECTION_TPL_IN, SECTION_TPL_OUT

logger = logging.getLogger(__name__)


class KeyboardHandler:

    def __init__(self):
        self.last_key = None

        self.__aliases = {}
        self.__keyboards = {}

        eh = doorpi.DoorPi().event_handler
        conf = doorpi.DoorPi().config
        kbnames = conf.get_keys(SECTION_KEYBOARDS)
        logger.info("Instantiating %d keyboard(s): %s", len(kbnames), ", ".join(kbnames))

        for kbname in kbnames:
            if kbname in self.__keyboards: raise ValueError(f"Duplicate keyboard name {kbname}")
            kbtype = conf.get_string(SECTION_KEYBOARDS, kbname)
            try:
                logger.debug("Instantiating keyboard %s (from_%s)", repr(kbname), kbtype)
                kb = importlib.import_module(f"doorpi.keyboard.from_{kbtype}").instantiate(kbname)
            except Exception:
                logger.exception("Failed to instantiate keyboard %s (%s)", repr(kbname), kbtype)
                continue
            self.__keyboards[kbname] = kb

            # register input pin actions
            logger.debug("Registering input pins for %s", repr(kbname))
            section = SECTION_TPL_IN.format(name=kbname)
            pins = conf.get_keys(section)
            for pin in pins:
                action = conf.get_string(section, pin)
                if action:
                    eh.register_action(f"OnKeyPressed_{kbname}.{pin}", action)

            # register output pin aliases
            logger.debug("Registering output pins for %s", repr(kbname))
            section = SECTION_TPL_OUT.format(name=kbname)
            pins = conf.get_keys(section)
            self.__aliases[kbname] = {}
            for pin in pins:
                alias = conf.get_string(section, pin)
                if not alias: alias = pin
                if alias in self.__aliases[kbname]:
                    raise ValueError(f"Duplicate pin alias {kbname}.{alias}")
                self.__aliases[kbname].update({alias: pin})

        num_fail = len(kbnames) - len(self.__keyboards)
        if num_fail != 0: raise RuntimeError(f"Failed to instantiate {num_fail} keyboards")

        eh.register_action("OnTimeTick", CallbackAction(self.self_check))

    def input(self, pinpath):
        try:
            kbname, pin = self._decode_pinpath(pinpath)
            return kb.input(pin)
        except KeyError:
            logger.exception("Cannot read input pin %s: unknown keyboard", pinpath)
        except Exception:
            logger.exception("Error reading from pin %s", pinpath)
        return False

    def output(self, pinpath, value):
        try:
            kbname, pinalias = self._decode_pinpath(pinpath)
            pin = self.__aliases[kbname][pinalias]
            return self.__keyboards[kbname].output(pin, value)
        except KeyError:
            logger.exception("Unknown keyboard or pin: %s", pinpath)
        except Exception:
            logger.exception("Cannot output to pin %s", pinpath)
        return False

    def self_check(self):
        abort = False
        for kbname, kb in self.__keyboards.items():
            try:
                kb.self_check()
            except Exception as ex:
                logger.exception("Keyboard %s failed self check", kbname)
                abort = True
        if abort:
            doorpi.DoorPi().doorpi_shutdown()

    def _enumerate_outputs(self):
        d = {}
        for kbname, kbaliases in self.__aliases.items():
            d.update({alias: f"{kbname}.{pin}" for alias, pin in kbaliases.items()})
        return d

    def _decode_pinpath(self, pinpath):
        try: kbname, pin = pinpath.split(".")
        except ValueError:
            raise ValueError(f"Cannot decode pin name {repr(pinpath)}") from None

        if not kbname:
            raise ValueError(f"Empty keyboard name given ({repr(pinpath)}")
        if not pin:
            raise ValueError(f"Empty pin alias given ({repr(pinpath)})")

        return (kbname, pin)
