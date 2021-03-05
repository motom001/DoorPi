"""Actions that control event execution: sleep, waitevent"""
import threading
from time import sleep
from typing import Any, Mapping

import doorpi.actions
import doorpi.event

from . import Action


class SleepAction(Action):
    """Delays event execution."""

    def __init__(self, time: str) -> None:
        super().__init__()
        self.__time = float(time)

    def __call__(self, event_id: str, extra: Mapping[str, Any]) -> None:
        sleep(self.__time)

    def __str__(self) -> str:
        return f"Wait for {self.__time} seconds"

    def __repr__(self) -> str:
        return f"sleep:{self.__time}"


class WaitEventAction(Action):
    """Waits for a different event to occur to perform an action."""

    def __init__(self, eventname: str, waittime: str, action: str) -> None:
        if action not in {"abort", "continue"}:
            raise ValueError("`action` must be `abort` or `continue`")

        self.__eventname = eventname
        self.__waittime = float(waittime)
        self.__action = action

        self.__flag = threading.Event()
        self.__cb = doorpi.actions.CallbackAction(self.__flag.set)
        doorpi.INSTANCE.event_handler.actions[eventname].insert(0, self.__cb)

    def __call__(self, event_id: str, extra: Mapping[str, Any]) -> None:
        self.__flag.clear()

        try:
            self.__flag.wait(self.__waittime)
        except TimeoutError:
            event_occured = False
        else:
            event_occured = True

        if (self.__action == "continue") ^ event_occured:
            raise doorpi.event.AbortEventExecution()

    def __str__(self) -> str:
        otheraction = "continue" if self.__action == "abort" else "abort"
        return "Wait for {}, then {} (otherwise {})".format(
            self.__eventname, self.__action, otheraction
        )

    def __repr__(self) -> str:
        return f"waitevent:{self.__eventname},{self.__action}"
