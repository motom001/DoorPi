"""Call related actions: call, file_call_value, hangup"""

import logging
import time
from pathlib import Path

import doorpi
from . import action


LOGGER = logging.getLogger(__name__)


@action("call")
class CallAction:
    """Calls a static number."""

    def __init__(self, url):
        self.__url = url

    def __call__(self, event_id, extra):
        doorpi.INSTANCE.sipphone.call(self.__url)

    def __str__(self):
        return f"Call {self.__url}"

    def __repr__(self):
        return f"call:{self.__url}"


@action("callf")
@action("file_call_value")
class CallFromFileAction:
    """Reads a number from a file and calls it."""

    def __init__(self, filename):
        self.__filename = Path(filename)
        if not self.__filename.exists():
            LOGGER.warning("File %s does not exist (yet?)", self.__filename)

    def __call__(self, event_id, extra):
        uri = self.__filename.read_text()
        if not uri:
            raise ValueError(f"File {self.__filename} is empty")
        doorpi.INSTANCE.sipphone.call(uri)

    def __str__(self):
        return f"Call the number stored in {self.__filename}"

    def __repr__(self):
        return f"file_call_value:{self.__filename}"


@action("hangup")
class HangupAction:
    """Hangs up all currently ongoing calls."""

    def __init__(self, waittime="0"):
        self.__waittime = float(waittime)

    def __call__(self, event_id, extra):
        if self.__waittime:
            LOGGER.info("[%s] Hanging up all calls in %s seconds", event_id, self.__waittime)
            time.sleep(self.__waittime)

        LOGGER.info("[%s] Hanging up all calls", event_id)
        doorpi.INSTANCE.sipphone.hangup()

    def __str__(self):
        return "Hang up all calls"

    def __repr__(self):
        return "hangup:"
