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
import os
import watchdog.events
import watchdog.observers

from time import sleep

import doorpi

from . import SECTION_TPL
from .abc import AbstractKeyboard

logger = logging.getLogger(__name__)


def instantiate(name): return FilesystemKeyboard(name)


class FilesystemKeyboard(AbstractKeyboard, watchdog.events.FileSystemEventHandler):

    def __init__(self, name):
        super().__init__(name)

        conf = doorpi.DoorPi().config
        section_name = SECTION_TPL.format(name=name)
        self.__reset_input = conf.get_bool(section_name, "reset_input", True)
        self.__base_path_input = conf.get_string_parsed(section_name, "base_path_input",
                                                        f"/run/doorpi/{name}/in")
        self.__base_path_output = conf.get_string_parsed(section_name, "base_path_output",
                                                         f"/run/doorpi/{name}/out")
        self.__input_states = dict.fromkeys(self._inputs, False)

        if not self.__base_path_input:
            raise ValueError(f"{self.name}: base_path_input must not be empty")
        if not self.__base_path_output:
            raise ValueError(f"{self.name}: base_path_output must not be empty")

        os.makedirs(self.__base_path_input, exist_ok=True)
        os.makedirs(self.__base_path_output, exist_ok=True)

        for input_pin in self._inputs:
            path = os.path.join(self.__base_path_input, input_pin)
            self.__write_file(path)
            os.chmod(path, 0o666)

        for output_pin in self._outputs:
            path = os.path.join(self.__base_path_output, output_pin)
            self.__write_file(path)
            os.chmod(path, 0o644)

        self.__observer = watchdog.observers.Observer()
        self.__observer.schedule(self, self.__base_path_input)
        self.__observer.start()

    def __del__(self):
        self._deactivate()
        doorpi.DoorPi().event_handler.unregister_source(self._event_source, True)

        for pin in self._inputs:
            try: os.remove(os.path.join(self.__base_path_input, pin))
            except FileNotFoundError: pass
            except Exception: logger.exception("%s: Unable to remove virtual input pin %s",
                                               self.name, pin)
        for pin in self._outputs:
            try: os.remove(os.path.join(self.__base_path_output, pin))
            except FileNotFoundError: pass
            except Exception: logger.exception("%s: Unable to remove virtual output pin %s",
                                               self.name, pin)
        super().__del__()

    def _deactivate(self):
        self.__observer.stop()
        self.__observer.join()
        super()._deactivate()

    def input(self, pin):
        if pin not in self._inputs: return False
        val = self.__read_file(os.path.join(self.__base_path_input, pin))
        if val is None:
            val = self.__input_states[pin]
            logger.debug("%s: File %s is empty, providing last known value (%s)",
                         self.name, pin, val)
        else:
            logger.debug("%s: Read %s from %s", self.name, val, pin)
            self.__input_states[pin] = val
        return val

    def output(self, pin, value):
        if pin not in self._outputs: return False
        logger.debug("%s: Setting pin %s to %s", self.name, pin, value)
        if self.__write_file(os.path.join(self.__base_path_output, pin), value):
            self._outputs[pin] = value
            return True
        else:
            return False

    def __read_file(self, pin):
        try:
            with open(pin, "r") as f:
                val = f.readline()
        except OSError:
            logger.exception("%s: Error reading pin %s", self.name, pin)
            return None
        if not val.strip(): return None
        else: return self._normalize(val)

    def __write_file(self, pin, value=False):
        value = self._normalize(value)
        try:
            with open(pin, "w") as f:
                f.write("1\n" if value else "0\n")
        except OSError:
            logger.exception("%s: Error setting pin %s to %s", self.name, pin, value)
            return False
        return True

    def on_modified(self, event):
        "Called by the watchdog library when an inotify event was triggered"

        if not isinstance(event, watchdog.events.FileModifiedEvent): return

        pin = os.path.basename(event.src_path)
        if pin not in self._inputs:
            logger.warning("%s: Received unsolicited FileModifiedEvent for %s",
                           self.name, event.src_path)
            return

        val = self.__read_file(event.src_path)

        if val is None:
            logger.debug("%s: Skipping FileModifiedEvent for %s, file is empty",
                         self.name, event.src_path)
            return

        if val == self.__input_states[pin]:
            logger.debug("%s: Skipping FileModifiedEvent for %s, logical value unchanged (%s)",
                         self.name, event.src_path, val)
            return

        self.__input_states[pin] = val
        if val:
            logger.info("%s: Pin %s flanked to logical TRUE, firing OnKeyDown",
                        self.name, pin)
            self._fire_OnKeyDown(pin)
            if self.__reset_input:
                self.__write_file(event.src_path, False)
        else:
            logger.info("%s: Pin %s flanked to logical FALSE, firing OnKeyUp",
                        self.name, pin)
            self._fire_OnKeyUp(pin)
