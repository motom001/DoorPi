from unittest.mock import patch

from doorpi.actions import control
from doorpi.event import AbortEventExecution

from ..mocks import DoorPi, DoorPiTestCase, assert_no_raise
from . import EVENT_EXTRA, EVENT_ID


class TestActionSleep(DoorPiTestCase):
    @patch("doorpi.actions.control.sleep")
    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_action(self, _, sleep):
        ac = control.SleepAction("5")
        ac(EVENT_ID, EVENT_EXTRA)
        sleep.assert_called_with(5.0)

    @patch("doorpi.actions.control.sleep")
    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_invalid_value(self, _1, _2):
        with self.assertRaises(ValueError):
            control.SleepAction("some string")


class TestWaitEvent(DoorPiTestCase):
    @patch("threading.Event")
    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_action_waits_for_the_specified_amount_of_time_if_no_events_are_fired(
        self, _, Event
    ):
        Event().wait.return_value = True
        ac = control.WaitEventAction("OtherEvent", "5", "continue")
        ac(EVENT_ID, EVENT_EXTRA)
        Event().wait.assert_called_with(5.0)

    @patch("threading.Event")
    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_firing_named_event_with_abort_aborts_event_execution(
        self, _, Event
    ):
        Event().wait.return_value = True
        ac = control.WaitEventAction("OtherEvent", "5", "abort")
        with self.assertRaises(AbortEventExecution):
            ac(EVENT_ID, EVENT_EXTRA)

    @patch("threading.Event")
    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_not_firing_named_event_with_abort_continues_event_execution(
        self, _, Event
    ):
        Event().wait.side_effect = TimeoutError
        ac = control.WaitEventAction("OtherEvent", "5", "abort")
        with assert_no_raise(self, cls=AbortEventExecution):
            ac(EVENT_ID, EVENT_EXTRA)

    @patch("threading.Event")
    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_firing_named_event_with_continue_continues_event_execution(
        self, _, Event
    ):
        Event().wait.return_value = True
        ac = control.WaitEventAction("OtherEvent", "5", "continue")
        with assert_no_raise(self, cls=AbortEventExecution):
            ac(EVENT_ID, EVENT_EXTRA)

    @patch("threading.Event")
    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_not_firing_named_event_with_continue_aborts_event_execution(
        self, _, Event
    ):
        Event().wait.side_effect = TimeoutError
        ac = control.WaitEventAction("OtherEvent", "5", "continue")
        with self.assertRaises(AbortEventExecution):
            ac(EVENT_ID, EVENT_EXTRA)
