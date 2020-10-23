from unittest.mock import patch, call, Mock
from datetime import datetime

from doorpi.actions import tick

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase

# The event source
ES = "doorpi.actions.tick"


class TestTickAction(DoorPiTestCase):

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_fire_yearly(self, instance):
        dtmock = Mock(wraps=datetime)
        dtmock.now.return_value = datetime(2001, 1, 1, 0, 0, 0)
        last = datetime(2000, 1, 1, 0, 0, 0)

        with patch("datetime.datetime", dtmock):
            tick.TickAction(str(last.timestamp()))(EVENT_ID, EVENT_EXTRA)

        eh = instance.event_handler
        self.assertEqual(eh.call_count, 2)
        eh.assert_has_calls(
            [call("OnTimeYear", ES), call("OnTimeYearOdd", ES)], any_order=True)

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_fire_monthly(self, instance):
        dtmock = Mock(wraps=datetime)
        dtmock.now.return_value = datetime(2000, 2, 1, 0, 0, 0)
        last = datetime(2000, 1, 1, 0, 0, 0)

        with patch("datetime.datetime", dtmock):
            tick.TickAction(last.timestamp())(EVENT_ID, EVENT_EXTRA)

        eh = instance.event_handler
        self.assertEqual(eh.call_count, 2)
        eh.assert_has_calls(
            [call("OnTimeMonth", ES), call("OnTimeMonthEven", ES)],
            any_order=True)

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_fire_daily(self, instance):
        dtmock = Mock(wraps=datetime)
        dtmock.now.return_value = datetime(2000, 1, 2, 0, 0, 0)
        last = datetime(2000, 1, 1, 0, 0, 0)

        with patch("datetime.datetime", dtmock):
            tick.TickAction(last.timestamp())(EVENT_ID, EVENT_EXTRA)

        eh = instance.event_handler
        self.assertEqual(eh.call_count, 2)
        eh.assert_has_calls(
            [call("OnTimeDay", ES), call("OnTimeDayEven", ES)], any_order=True)

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_fire_hourly(self, instance):
        dtmock = Mock(wraps=datetime)
        dtmock.now.return_value = datetime(2000, 1, 1, 1, 0, 0)
        last = datetime(2000, 1, 1, 0, 0, 0)

        with patch("datetime.datetime", dtmock):
            tick.TickAction(last.timestamp())(EVENT_ID, EVENT_EXTRA)

        eh = instance.event_handler
        self.assertEqual(eh.call_count, 3)
        eh.assert_has_calls([
            call("OnTimeHour", ES),
            call("OnTimeHourOdd", ES),
            call("OnTimeHour01", ES),
        ], any_order=True)

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_fire_minutely(self, instance):
        dtmock = Mock(wraps=datetime)
        dtmock.now.return_value = datetime(2000, 1, 1, 0, 1, 0)
        last = datetime(2000, 1, 1, 0, 0, 0)

        with patch("datetime.datetime", dtmock):
            tick.TickAction(last.timestamp())(EVENT_ID, EVENT_EXTRA)

        eh = instance.event_handler
        self.assertEqual(eh.call_count, 3)
        eh.assert_has_calls([
            call("OnTimeMinute", ES),
            call("OnTimeMinuteOdd", ES),
            call("OnTimeMinute01", ES),
        ], any_order=True)

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_fire_secondly(self, instance):
        dtmock = Mock(wraps=datetime)
        dtmock.now.return_value = datetime(2000, 1, 1, 0, 0, 1)
        last = datetime(2000, 1, 1, 0, 0, 0)

        with patch("datetime.datetime", dtmock):
            tick.TickAction(last.timestamp())(EVENT_ID, EVENT_EXTRA)

        eh = instance.event_handler
        self.assertEqual(eh.call_count, 3)
        eh.assert_has_calls([
            call("OnTimeSecond", ES),
            call("OnTimeSecondOdd", ES),
            call("OnTimeSecond01", ES),
        ], any_order=True)
