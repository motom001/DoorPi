"""Actions that control event execution: sleep"""
from time import sleep
from typing import Any, Mapping

from . import Action, action


@action("sleep")
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
