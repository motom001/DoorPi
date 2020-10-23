"""The internal tick action."""
import datetime
from typing import Any, Mapping

import doorpi
from . import Action, CallbackAction, action


@action("time_tick")
class TickAction(Action):
    """The internal tick action."""
    def __init__(self, last_tick: str) -> None:
        super().__init__()
        self.__last_tick = datetime.datetime.fromtimestamp(float(last_tick))

        eh = doorpi.INSTANCE.event_handler
        if __name__ in eh.sources:
            raise RuntimeError("Attempt to instantiate multiple TickActions")
        eh.register_source(__name__)
        eh.register_action("OnShutdown", CallbackAction(
            eh.unregister_source, __name__, force=True))

        for i in ("Second", "Minute", "Hour", "Day", "Week", "Month", "Year"):
            eh.register_event(f"OnTime{i}", __name__)
            eh.register_event(f"OnTime{i}Even", __name__)
            eh.register_event(f"OnTime{i}Odd", __name__)

        for i in ("Second", "Minute"):
            for j in range(60):
                eh.register_event(f"OnTime{i}{j:02}", __name__)

        for j in range(24):
            eh.register_event(f"OnTimeHour{j:02}", __name__)

    def __call__(self, event_id: str, extra: Mapping[str, Any]) -> None:
        now = datetime.datetime.now()

        if now.year != self.__last_tick.year:
            self._fire_event("Year", now.year)
        if now.month != self.__last_tick.month:
            self._fire_event("Month", now.month)
        if now.day != self.__last_tick.day:
            self._fire_event("Day", now.day)
        if now.hour != self.__last_tick.hour:
            self._fire_event_numbered("Hour", now.hour)
        if now.minute != self.__last_tick.minute:
            self._fire_event_numbered("Minute", now.minute)
        if now.second != self.__last_tick.second:
            self._fire_event_numbered("Second", now.second)

        self.__last_tick = now

    @staticmethod
    def _fire_event(event: str, num: int) -> None:
        eh = doorpi.INSTANCE.event_handler
        eh(f"OnTime{event}", __name__)
        eh(f"OnTime{event}{('Even', 'Odd')[num % 2]}", __name__)

    @classmethod
    def _fire_event_numbered(cls, event: str, num: int) -> None:
        cls._fire_event(event, num)
        doorpi.INSTANCE.event_handler(f"OnTime{event}{num:02}", __name__)

    def __str__(self) -> str:
        return "Perform regular housekeeping tasks"

    def __repr__(self) -> str:
        return "<internal tick>"
