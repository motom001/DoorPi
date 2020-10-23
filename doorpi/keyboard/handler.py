"""This module houses the keyboard handler."""
import importlib
import logging
from typing import Any, Dict, Optional, Tuple

import doorpi.actions
import doorpi.keyboard.abc

LOGGER = logging.getLogger(__name__)


class KeyboardHandler:
    """The keyboard handler.

    This class is responsible for constructing the individual keyboard
    instances, dispatching output events to and querying inputs from them.
    """

    last_key: Optional[str]

    __aliases: Dict[str, Dict[str, str]]
    __keyboards: Dict[str, doorpi.keyboard.abc.AbstractKeyboard]

    def __init__(self) -> None:
        self.last_key = None

        self.__aliases = {}
        self.__keyboards = {}

        eh = doorpi.INSTANCE.event_handler
        conf = doorpi.INSTANCE.config.view("keyboard")
        LOGGER.info(
            "Instantiating %d keyboard(s): %s",
            len(conf),
            ", ".join(conf.keys()),
        )

        for kbname in conf.keys():
            kbtype = conf[kbname, "type"].name
            LOGGER.debug("Instantiating keyboard %r (from_%s)", kbname, kbtype)

            self.__keyboards[kbname] = kb = importlib.import_module(
                f"doorpi.keyboard.from_{kbtype}"
            ).instantiate(
                kbname
            )  # type: ignore[attr-defined]

            LOGGER.debug("Registering input pins for %r", kbname)
            for pin, actions in kb.config.view("input").items():
                for action in actions:
                    if action:
                        eh.register_action(
                            f"OnKeyPressed_{kbname}.{pin}", action
                        )

            LOGGER.debug("Registering output pins for %r", kbname)
            self.__aliases[kbname] = {}
            for pin, alias in kb.config.view("output").items():
                if not alias:
                    alias = pin
                if alias in self.__aliases[kbname]:
                    raise ValueError(f"Duplicate pin alias {kbname}.{alias}")
                self.__aliases[kbname][alias] = pin

        eh.register_action(
            "OnTimeTick", doorpi.actions.CheckAction(self.self_check)
        )

    def input(self, pinpath: str) -> bool:
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

    def output(self, pinpath: str, value: Any) -> bool:
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

    def self_check(self) -> None:
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
            doorpi.INSTANCE.doorpi_shutdown()

    def enumerate_outputs(self) -> Dict[str, str]:
        """Enumerates all known output pins

        Returns:
            A dict mapping pin aliases to the fully qualified pin names
        """
        pins = {}
        for kbname, kbaliases in self.__aliases.items():
            pins.update(
                {alias: f"{kbname}.{pin}" for alias, pin in kbaliases.items()}
            )
        return pins

    def _decode_pinpath(
        self,
        pinpath: str,
    ) -> Tuple[doorpi.keyboard.abc.AbstractKeyboard, str, str]:
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
