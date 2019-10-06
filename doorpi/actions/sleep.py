from time import sleep

from . import Action


class SleepAction(Action):
    def __init__(self, time):
        self.__time = float(time)

    def __call__(self, event_id, extra):
        sleep(self.__time)

    def __str__(self):
        return f"Wait for {self.__time} seconds"

    def __repr__(self):
        return f"{__name__.split('.')[-1]}:{self.__time}"


instantiate = SleepAction
