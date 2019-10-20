import datetime
import logging
import time

import doorpi
from . import Action, CallbackAction


logger = logging.getLogger(__name__)


class TickAction(Action):

    def __init__(self, last_tick):
        self.__last_tick = datetime.datetime.fromtimestamp(float(last_tick))

        eh = doorpi.DoorPi().event_handler
        if __name__ in eh.sources:
            raise RuntimeError("Attempt to instatiate multiple TickActions")
        eh.register_source(__name__)
        eh.register_action("OnShutdown", CallbackAction(self.__del__))

        for i in ("Second", "Minute", "Hour", "Day", "Week", "Month", "Year"):
            eh.register_event(f"OnTime{i}", __name__)
            eh.register_event(f"OnTime{i}Even", __name__)
            eh.register_event(f"OnTime{i}Odd", __name__)

        for i in ("Second", "Minute"):
            for j in range(60):
                eh.register_event(f"OnTime{i}{j:02}", __name__)

        for i in range(24):
            eh.register_event(f"OnTimeHour{i:02}", __name__)

    def __del__(self):
        doorpi.DoorPi().event_handler.unregister_source(__name__, force=True)

    def __call__(self, event_id, extra):
        now = datetime.datetime.now()

        if now.year != self.__last_tick.year: self.fire_event("Year", now.year)
        if now.month != self.__last_tick.month: self.fire_event("Month", now.month)
        if now.day != self.__last_tick.day: self.fire_event("Day", now.day)
        if now.hour != self.__last_tick.hour: self.fire_event_numbered("Hour", now.hour)
        if now.minute != self.__last_tick.minute: self.fire_event_numbered("Minute", now.minute)
        if now.second != self.__last_tick.second: self.fire_event_numbered("Second", now.second)

        self.__last_tick = now

    def fire_event(self, ev, num):
        eh = doorpi.DoorPi().event_handler
        eh(f"OnTime{ev}", __name__)
        eh(f"OnTime{ev}{'Even' if num % 2 == 0 else 'Odd'}", __name__)

    def fire_event_numbered(self, ev, num):
        self.fire_event(ev, num)
        doorpi.DoorPi().event_handler(f"OnTime{ev}{num:02}", __name__)


instantiate = TickAction
