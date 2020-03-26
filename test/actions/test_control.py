from unittest.mock import patch

from doorpi.actions import control

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase


class TestActionSleep(DoorPiTestCase):

    @patch("doorpi.actions.control.sleep")
    @patch("doorpi.DoorPi", DoorPi)
    def test_action(self, sleep):
        ac = control.SleepAction("5")
        ac(EVENT_ID, EVENT_EXTRA)
        sleep.assert_called_with(5.0)

    @patch("doorpi.actions.control.sleep")
    @patch("doorpi.DoorPi", DoorPi)
    def test_invalid_value(self, sleep):
        del sleep
        with self.assertRaises(ValueError):
            control.SleepAction("some string")
