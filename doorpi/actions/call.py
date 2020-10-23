"""Call related actions: call, file_call_value, hangup"""

import logging
import pathlib
import time
from typing import Any, Mapping

import doorpi

from . import Action, action

LOGGER = logging.getLogger(__name__)


@action("call")
class CallAction(Action):
    """Calls a static number."""

    def __init__(self, url: str) -> None:
        super().__init__()
        self.__url = url

    def __call__(self, event_id: str, extra: Mapping[str, Any]) -> None:
        doorpi.INSTANCE.sipphone.call(self.__url)

    def __str__(self) -> str:
        return f"Call {self.__url}"

    def __repr__(self) -> str:
        return f"call:{self.__url}"


@action("callf")
@action("file_call_value")
class CallFromFileAction(Action):
    """Reads a number from a file and calls it."""

    def __init__(self, filename: str) -> None:
        super().__init__()
        self.__filename = pathlib.Path(filename)
        if not self.__filename.exists():
            LOGGER.warning("File %s does not exist (yet?)", self.__filename)

    def __call__(self, event_id: str, extra: Mapping[str, Any]) -> None:
        uri = self.__filename.read_text()
        if not uri:
            raise ValueError(f"File {self.__filename} is empty")
        doorpi.INSTANCE.sipphone.call(uri)

    def __str__(self) -> str:
        return f"Call the number stored in {self.__filename}"

    def __repr__(self) -> str:
        return f"file_call_value:{self.__filename}"


@action("hangup")
class HangupAction(Action):
    """Hangs up all currently ongoing calls."""

    def __init__(self, waittime: str = "0") -> None:
        super().__init__()
        self.__waittime = float(waittime)

    def __call__(self, event_id: str, extra: Mapping[str, Any]) -> None:
        if self.__waittime:
            LOGGER.info(
                "[%s] Hanging up all calls in %s seconds",
                event_id,
                self.__waittime,
            )
            time.sleep(self.__waittime)

        LOGGER.info("[%s] Hanging up all calls", event_id)
        doorpi.INSTANCE.sipphone.hangup()

    def __str__(self) -> str:
        return "Hang up all calls"

    def __repr__(self) -> str:
        return "hangup:"
