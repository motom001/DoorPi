from unittest.mock import patch, call, Mock
from datetime import datetime

from doorpi.actions import tick

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase


# The event source
ES = "doorpi.actions.tick"


@patch("doorpi.actions.tick.TickAction.__del__", Mock())
class TestTickAction(DoorPiTestCase):

    @patch("doorpi.DoorPi", DoorPi)
    def test_fire_yearly(self):
        dtmock = Mock(wraps=datetime)
        dtmock.now.return_value = datetime(2001, 1, 1, 0, 0, 0)
        last = datetime(2000, 1, 1, 0, 0, 0)

        with patch("datetime.datetime", dtmock):
            tick.TickAction(str(last.timestamp()))(EVENT_ID, EVENT_EXTRA)

        eh = DoorPi().event_handler
        self.assertEqual(eh.call_count, 2)
        eh.assert_has_calls(
            [call("OnTimeYear", ES), call("OnTimeYearOdd", ES)], any_order=True)

    @patch("doorpi.DoorPi", DoorPi)
    def test_fire_monthly(self):
        dtmock = Mock(wraps=datetime)
        dtmock.now.return_value = datetime(2000, 2, 1, 0, 0, 0)
        last = datetime(2000, 1, 1, 0, 0, 0)

        with patch("datetime.datetime", dtmock):
            tick.TickAction(last.timestamp())(EVENT_ID, EVENT_EXTRA)

        eh = DoorPi().event_handler
        self.assertEqual(eh.call_count, 2)
        eh.assert_has_calls(
            [call("OnTimeMonth", ES), call("OnTimeMonthEven", ES)], any_order=True)

    @patch("doorpi.DoorPi", DoorPi)
    def test_fire_daily(self):
        dtmock = Mock(wraps=datetime)
        dtmock.now.return_value = datetime(2000, 1, 2, 0, 0, 0)
        last = datetime(2000, 1, 1, 0, 0, 0)

        with patch("datetime.datetime", dtmock):
            tick.TickAction(last.timestamp())(EVENT_ID, EVENT_EXTRA)

        eh = DoorPi().event_handler
        self.assertEqual(eh.call_count, 2)
        eh.assert_has_calls(
            [call("OnTimeDay", ES), call("OnTimeDayEven", ES)], any_order=True)

    @patch("doorpi.DoorPi", DoorPi)
    def test_fire_hourly(self):
        dtmock = Mock(wraps=datetime)
        dtmock.now.return_value = datetime(2000, 1, 1, 1, 0, 0)
        last = datetime(2000, 1, 1, 0, 0, 0)

        with patch("datetime.datetime", dtmock):
            tick.TickAction(last.timestamp())(EVENT_ID, EVENT_EXTRA)

        eh = DoorPi().event_handler
        self.assertEqual(eh.call_count, 3)
        eh.assert_has_calls(
            [call("OnTimeHour", ES), call("OnTimeHourOdd", ES), call("OnTimeHour01", ES)],
            any_order=True)

    @patch("doorpi.DoorPi", DoorPi)
    def test_fire_minutely(self):
        dtmock = Mock(wraps=datetime)
        dtmock.now.return_value = datetime(2000, 1, 1, 0, 1, 0)
        last = datetime(2000, 1, 1, 0, 0, 0)

        with patch("datetime.datetime", dtmock):
            tick.TickAction(last.timestamp())(EVENT_ID, EVENT_EXTRA)

        eh = DoorPi().event_handler
        self.assertEqual(eh.call_count, 3)
        eh.assert_has_calls(
            [call("OnTimeMinute", ES), call("OnTimeMinuteOdd", ES), call("OnTimeMinute01", ES)],
            any_order=True)

    @patch("doorpi.DoorPi", DoorPi)
    def test_fire_secondly(self):
        dtmock = Mock(wraps=datetime)
        dtmock.now.return_value = datetime(2000, 1, 1, 0, 0, 1)
        last = datetime(2000, 1, 1, 0, 0, 0)

        with patch("datetime.datetime", dtmock):
            tick.TickAction(last.timestamp())(EVENT_ID, EVENT_EXTRA)

        eh = DoorPi().event_handler
        self.assertEqual(eh.call_count, 3)
        eh.assert_has_calls(
            [call("OnTimeSecond", ES), call("OnTimeSecondOdd", ES), call("OnTimeSecond01", ES)],
            any_order=True)
