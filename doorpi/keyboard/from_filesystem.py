"""The file-based pseudo keyboard

This keyboard module simulates input/output events by using files. This
may be useful for triggering events remotely via SSH, integrating with
other software suites, or for testing purposes.

Requirements
************

- The `watchdog` python module
- Write access to an arbitrary directory

  > **Note**: Using files on a persistent filesystem is not recommended,
  > as it actively degrades the life time of flash media like SD cards.
  > Consider using paths on tmpfs filesystems, like `/run` or `/tmp`.

Usage
*****

1. Create a keyboard of type "filesystem"
2. In its settings section, set `base_path_input` and
   `base_path_output` to the directory paths where the input/output
   files should be created. The two directories should be different.
   The default values are `/run/doorpi/<keyboard_name>/in` for input
   and `/run/doorpi/<keyboard_name>/out` for output files. The
   directories configured here will be created if they do not already
   exist, as long as DoorPi has the permissions necessary to do so.

   If `reset_input` is set to True (default), the input files will be
   reset to (logical) false after being read. Whether that corresponds
   to the value True or False depends on the value of `polarity`. Set
   `reset_input` to False to disable this behavior.
3. Define the keyboard's input/output pins and their actions as normal.
   The names of the pins will be used as file names. You do not need
   to specify aliases for output pins, as they default to the pin name.

After starting, the keyboard module will create the directories and
files according to its configuration. Each file will initially contain
the word "False" (or "True" if the keyboard's polarity is LOW). DoorPi
will then start watching for changes to the input files and write out
output pin states to the output files.

DoorPi itself will only write out "True" or "False" for the pin states
"high" and "low" respectively, but it recognizes a few more values in
input files. For a full list of all possible "high" values, see the
"HIGH_LEVEL" list in `doorpi/keyboard/__init__.py`. Everything that is
not "high" will be recognized as "low", except for empty files which
will retain their previous logical pin state.

Events will only be triggered if the logical pin state changes. If a
"high" value is written to a file that contains a different "high"
value, no event will be triggered. The same applies for "low" values.
"""
import logging
import pathlib
from typing import Any, Literal, Optional

import watchdog.events
import watchdog.observers

import doorpi

from .abc import AbstractKeyboard

LOGGER = logging.getLogger(__name__)


class FilesystemKeyboard(
    AbstractKeyboard, watchdog.events.FileSystemEventHandler
):
    def __init__(self, name: str) -> None:
        super().__init__(name)

        self.__reset_input = self.config["reset_input"]
        self.__base_path_input = self.config["inputdir"]
        self.__base_path_output = self.config["outputdir"]
        self.__input_states = dict.fromkeys(self._inputs, False)

        if not self.__base_path_input:
            raise ValueError(f"{self.name}: base_path_input must not be empty")
        if not self.__base_path_output:
            raise ValueError(
                f"{self.name}: base_path_output must not be empty"
            )

        self.__base_path_input.mkdir(parents=True, exist_ok=True)
        self.__base_path_output.mkdir(parents=True, exist_ok=True)

        for pin in self._inputs:
            pinfile = self.__base_path_input / pin
            self.__write_file(pinfile)
            pinfile.chmod(0o666)

        for pin in self._outputs:
            pinfile = self.__base_path_output / pin
            self.__write_file(pinfile)
            pinfile.chmod(0o644)

        self.__observer = watchdog.observers.Observer()
        self.__observer.schedule(self, str(self.__base_path_input))
        self.__observer.start()

    def destroy(self) -> None:
        # pylint: disable=broad-except
        self._deactivate()
        doorpi.INSTANCE.event_handler.unregister_source(
            self._event_source, force=True
        )

        for pin in self._inputs:
            try:
                (self.__base_path_input / pin).unlink()
            except FileNotFoundError:
                pass
            except Exception:
                LOGGER.exception(
                    "%s: Unable to unlink virtual input pin %s", self.name, pin
                )
        for pin in self._outputs:
            try:
                (self.__base_path_output / pin).unlink()
            except FileNotFoundError:
                pass
            except Exception:
                LOGGER.exception(
                    "%s: Unable to unlink virtual output pin %s",
                    self.name,
                    pin,
                )

        for pindir in (self.__base_path_input, self.__base_path_output):
            try:
                pindir.rmdir()
            except Exception as ex:
                LOGGER.error(
                    "%s: Cannot remove directory %s: %s", self.name, pindir, ex
                )
        super().destroy()

    def _deactivate(self) -> None:
        self.__observer.stop()
        self.__observer.join()
        super()._deactivate()

    def input(self, pin: str) -> bool:
        super().input(pin)
        val = self.__read_file(self.__base_path_input / pin)
        if val is None:
            val = self.__input_states[pin]
            LOGGER.debug(
                "%s: File %s is empty, providing last known value (%s)",
                self.name,
                pin,
                val,
            )
        else:
            LOGGER.debug("%s: Read %s from %s", self.name, val, pin)
            self.__input_states[pin] = val
        return val

    def output(self, pin: str, value: Any) -> bool:
        super().output(pin, value)
        LOGGER.debug("%s: Setting pin %s to %s", self.name, pin, value)
        if self.__write_file(self.__base_path_output / pin, value):
            self._outputs[pin] = value
            return True
        return False

    def __read_file(self, pin: pathlib.Path) -> Optional[bool]:
        try:
            val = pin.read_text()
        except OSError as err:
            LOGGER.warning(
                "%s: Cannot read from pin %s: %s: %s",
                self.name,
                pin,
                type(err).__name__,
                err,
            )
            return None
        valwords = val.strip().split()
        if not valwords or not valwords[0]:
            return None
        return self._normalize(valwords[0])

    def __write_file(
        self, pin: pathlib.Path, value: Any = False
    ) -> Literal[True]:
        value = self._normalize(value)
        try:
            pin.write_text("1\n" if value else "0\n")
        except OSError as err:
            LOGGER.error(
                "%s: Cannot write to pin %s: %s: %s",
                self.name,
                pin,
                type(err).__name__,
                err,
            )
        return True

    def on_modified(self, event: watchdog.events.FileSystemEvent) -> None:
        "Called by the watchdog library when an inotify event was triggered"
        if not isinstance(event, watchdog.events.FileModifiedEvent):
            return

        pin = pathlib.Path(event.src_path)
        if (
            pin.name not in self._inputs
            or pin.parent != self.__base_path_input
        ):
            LOGGER.warning(
                "%s: Received unsolicited FileModifiedEvent for %s",
                self.name,
                event.src_path,
            )
            return

        val = self.__read_file(pin)

        if val is None:
            LOGGER.debug(
                "%s: Skipping FileModifiedEvent for %s, file is empty",
                self.name,
                pin,
            )
            return

        if val == self.__input_states[pin.name]:
            LOGGER.debug(
                "%s: Skipping FileModifiedEvent for %s,"
                " as the logical value has not changed (%s)",
                self.name,
                pin,
                val,
            )
            return

        self.__input_states[pin.name] = val
        if val:
            LOGGER.info(
                "%s: Pin %s flanked to logical TRUE, firing OnKeyDown",
                self.name,
                pin.name,
            )
            self._fire_keydown(pin.name)
            if self.__reset_input:
                self.__write_file(pin, False)
        else:
            LOGGER.info(
                "%s: Pin %s flanked to logical FALSE, firing OnKeyUp",
                self.name,
                pin,
            )
            self._fire_keyup(pin.name)


instantiate = FilesystemKeyboard  # pylint: disable=invalid-name
