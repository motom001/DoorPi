from time import sleep

from . import Action


class SleepAction(Action):
    def __init__(self, time):
        self.__time = float(time)

    def __call__(self, event_id, extra):
        sleep(self.__time)


instantiate = SleepAction
