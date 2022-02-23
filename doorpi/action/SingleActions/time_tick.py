# -*- coding: utf-8 -*-
import doorpi
from doorpi.action.base import SingleAction

import time
import datetime

import logging
logger = logging.getLogger(__name__)
logger.debug('%s loaded', __name__)

MINUTE_RANGE = list(range(0, 60))
HOUR_RANGE = list(range(0, 23))
last_time_tick_second = 0


def destroy_time_tick():
    doorpi.DoorPi().event_handler.unregister_source(__name__, True)


def time_tick(last_tick):
    global last_time_tick_second
    timestamp_now = time.time()
    timestamp_past = last_time_tick_second

    datetime_now = datetime.datetime.fromtimestamp(timestamp_now)
    datetime_past = datetime.datetime.fromtimestamp(timestamp_past)

    if datetime_now.year != datetime_past.year:
        doorpi.DoorPi().event_handler('OnTimeYear', __name__)
        if datetime_now.year % 2 is 0:
            doorpi.DoorPi().event_handler('OnTimeYearEvenNumber', __name__)
        else:
            doorpi.DoorPi().event_handler('OnTimeYearUnevenNumber', __name__)

    if datetime_now.month != datetime_past.month:
        doorpi.DoorPi().event_handler('OnTimeMonth', __name__)
        if datetime_now.month % 2 is 0:
            doorpi.DoorPi().event_handler('OnTimeMonthEvenNumber', __name__)
        else:
            doorpi.DoorPi().event_handler('OnTimeMonthUnevenNumber', __name__)

    if datetime_now.day != datetime_past.day:
        doorpi.DoorPi().event_handler('OnTimeDay', __name__)
        if datetime_now.day % 2 is 0:
            doorpi.DoorPi().event_handler('OnTimeDayEvenNumber', __name__)
        else:
            doorpi.DoorPi().event_handler('OnTimeDayUnevenNumber', __name__)

    if datetime_now.hour != datetime_past.hour:
        doorpi.DoorPi().event_handler('OnTimeHour', __name__)
        if datetime_now.hour % 2 is 0:
            doorpi.DoorPi().event_handler('OnTimeHourEvenNumber', __name__)
        else:
            doorpi.DoorPi().event_handler('OnTimeHourUnevenNumber', __name__)

        for hour in HOUR_RANGE:
            if hour is datetime_now.hour:
                doorpi.DoorPi().event_handler(('OnTimeHour{0}').format(hour), __name__)

    if datetime_now.minute != datetime_past.minute:
        doorpi.DoorPi().event_handler('OnTimeMinute', __name__)
        if datetime_now.minute % 2 is 0:
            doorpi.DoorPi().event_handler('OnTimeMinuteEvenNumber', __name__)
        else:
            doorpi.DoorPi().event_handler('OnTimeMinuteUnevenNumber', __name__)

        for minute in MINUTE_RANGE:
            if minute is datetime_now.minute:
                doorpi.DoorPi().event_handler(('OnTimeMinute{0}').format(minute), __name__)

        if datetime_now.minute % 5 is 0:
            doorpi.DoorPi().event_handler('OnTimeMinuteEvery5', __name__)

    if datetime_now.second != datetime_past.second:
        doorpi.DoorPi().event_handler('OnTimeSecond', __name__)
        if datetime_now.second % 2 is 0:
            doorpi.DoorPi().event_handler('OnTimeSecondEvenNumber', __name__)
        else:
            doorpi.DoorPi().event_handler('OnTimeSecondUnevenNumber', __name__)

    last_time_tick_second = timestamp_now
    return True


def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) is not 1:
        return None

    last_tick = parameter_list[0]

    # register timebased_events
    for i in ('Second', 'Minute', 'Hour', 'Day', 'Week', 'Month', 'Year'):
        doorpi.DoorPi().event_handler.register_event(f'OnTime{i}', __name__)
        doorpi.DoorPi().event_handler.register_event(f'OnTime{i}EvenNumber', __name__)
        doorpi.DoorPi().event_handler.register_event(f'OnTime{i}UnevenNumber', __name__)

    for minute in MINUTE_RANGE:
        doorpi.DoorPi().event_handler.register_event(('OnTimeMinute{0}').format(minute), __name__)
    doorpi.DoorPi().event_handler.register_event('OnTimeMinuteEvery5', __name__)

    for hour in HOUR_RANGE:
        doorpi.DoorPi().event_handler.register_event(('OnTimeHour{0}').format(hour), __name__)

    doorpi.DoorPi().event_handler.register_action('OnShutdown', TimeTickDestroyAction(destroy_time_tick))

    return TimeTickAction(time_tick, last_tick)


class TimeTickAction(SingleAction):
    pass


class TimeTickDestroyAction(SingleAction):
    pass
