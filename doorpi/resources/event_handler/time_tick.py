# -*- coding: utf-8 -*-

from main import DOORPI
logger = DOORPI.register_module(__name__, return_new_logger = True)

import time
import datetime
from resources.event_handler.classes import SingleAction
class TimeTickDestroyAction(SingleAction): pass

class TimeTicker:
    last_time_tick = 0
    last_realtime_event = 0
    
    def start(self):
        # register timebased_events
        DOORPI.events.register_event('OnTimeTick', __name__)

        DOORPI.events.register_event('OnTimeSecond', __name__)
        DOORPI.events.register_event('OnTimeSecondEvenNumber', __name__)
        DOORPI.events.register_event('OnTimeSecondUnevenNumber', __name__)

        DOORPI.events.register_event('OnTimeMinute', __name__)
        DOORPI.events.register_event('OnTimeMinuteEvenNumber', __name__)
        DOORPI.events.register_event('OnTimeMinuteUnevenNumber', __name__)
        for minute in DOORPI.CONST.MINUTE_RANGE:
            DOORPI.events.register_event('OnTimeMinute%s'%minute, __name__)
        DOORPI.events.register_event('OnTimeMinuteEvery5', __name__)

        DOORPI.events.register_event('OnTimeHour', __name__)
        DOORPI.events.register_event('OnTimeHourEvenNumber', __name__)
        DOORPI.events.register_event('OnTimeHourUnevenNumber', __name__)
        for hour in DOORPI.CONST.HOUR_RANGE:
            DOORPI.events.register_event('OnTimeHour%s'%hour, __name__)

        DOORPI.events.register_event('OnTimeDay', __name__)
        DOORPI.events.register_event('OnTimeDayEvenNumber', __name__)
        DOORPI.events.register_event('OnTimeDayUnevenNumber', __name__)

        DOORPI.events.register_event('OnTimeWeek', __name__)
        DOORPI.events.register_event('OnTimeWeekEvenNumber', __name__)
        DOORPI.events.register_event('OnTimeWeekUnevenNumber', __name__)

        DOORPI.events.register_event('OnTimeMonth', __name__)
        DOORPI.events.register_event('OnTimeMonthEvenNumber', __name__)
        DOORPI.events.register_event('OnTimeMonthUnevenNumber', __name__)

        DOORPI.events.register_event('OnTimeYear', __name__)
        DOORPI.events.register_event('OnTimeYearEvenNumber', __name__)
        DOORPI.events.register_event('OnTimeYearUnevenNumber', __name__)

        DOORPI.events.register_action('OnShutdown', TimeTickDestroyAction(self.stop))
        return self

    def stop(self):
        DOORPI.events.unregister_source(__name__, True)

    def do_tick_tack(self, time_for_this_tick = 0.2):

        timestamp_now = time.time()
        timestamp_past = self.last_time_tick

        datetime_now = datetime.datetime.fromtimestamp(timestamp_now)
        datetime_past = datetime.datetime.fromtimestamp(timestamp_past)

        if datetime_now.year != datetime_past.year:
            DOORPI.events('OnTimeYear', __name__)
            if datetime_now.year % 2 is 0:      DOORPI.events('OnTimeYearEvenNumber', __name__)
            else:                               DOORPI.events('OnTimeYearUnevenNumber', __name__)

        if datetime_now.month != datetime_past.month:
            DOORPI.events('OnTimeMonth', __name__)
            if datetime_now.month % 2 is 0:     DOORPI.events('OnTimeMonthEvenNumber', __name__)
            else:                               DOORPI.events('OnTimeMonthUnevenNumber', __name__)

        if datetime_now.day != datetime_past.day:
            DOORPI.events('OnTimeDay', __name__)
            if datetime_now.day % 2 is 0:       DOORPI.events('OnTimeDayEvenNumber', __name__)
            else:                               DOORPI.events('OnTimeDayUnevenNumber', __name__)

        if datetime_now.hour != datetime_past.hour:
            DOORPI.events('OnTimeHour', __name__)
            if datetime_now.hour % 2 is 0:      DOORPI.events('OnTimeHourEvenNumber', __name__)
            else:                               DOORPI.events('OnTimeHourUnevenNumber', __name__)

            for hour in DOORPI.CONST.HOUR_RANGE:
                if hour is datetime_now.hour:   DOORPI.events('OnTimeHour%s'%hour, __name__)

        if datetime_now.minute != datetime_past.minute:
            DOORPI.events('OnTimeMinute', __name__)
            if datetime_now.minute % 2 is 0:    DOORPI.events('OnTimeMinuteEvenNumber', __name__)
            else:                               DOORPI.events('OnTimeMinuteUnevenNumber', __name__)

            for minute in DOORPI.CONST.MINUTE_RANGE:
                if minute is datetime_now.minute: DOORPI.events('OnTimeMinute%s'%minute, __name__)

            if datetime_now.minute % 5 is 0:    DOORPI.events('OnTimeMinuteEvery5', __name__)

        if datetime_now.second != datetime_past.second:
            DOORPI.events('OnTimeSecond', __name__)
            if datetime_now.second % 2 is 0:    DOORPI.events('OnTimeSecondEvenNumber', __name__)
            else:                               DOORPI.events('OnTimeSecondUnevenNumber', __name__)

        microsecond = datetime_now.microsecond / 100000
        if (microsecond % 2 is 0 or microsecond is 0) and microsecond is not self.last_realtime_event:
            self.last_realtime_event = microsecond
            DOORPI.events('OnTimeTick', __name__)

        self.last_time_tick = timestamp_now
        sleep_time = time_for_this_tick - (timestamp_now - time.time())
        if sleep_time > 0: time.sleep(sleep_time)


        return True
