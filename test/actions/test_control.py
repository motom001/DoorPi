from unittest.mock import patch

from doorpi.actions import control

from ..mocks import DoorPi, DoorPiTestCase
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
