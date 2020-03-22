"""Actions that control event execution: sleep"""
from time import sleep

from . import action


@action("sleep")
class SleepAction:
    """Delays event execution."""

    def __init__(self, time):
        self.__time = float(time)

    def __call__(self, event_id, extra):
        sleep(self.__time)

    def __str__(self):
        return f"Wait for {self.__time} seconds"

    def __repr__(self):
        return f"sleep:{self.__time}"
