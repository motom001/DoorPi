from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase
from unittest.mock import patch

import doorpi
import doorpi.actions.out as action


PIN = "kb.pin"
START = 1
STOP = 0
HOLD = 5


class TestActionCall(DoorPiTestCase):

    @patch('doorpi.DoorPi', DoorPi)
    def test_argvalidation(self):
        with self.assertRaises(ValueError):
            action.instantiate(PIN, START, STOP, "invalid")

    @patch('doorpi.DoorPi', DoorPi)
    def test_normal(self):
        ac = action.instantiate(PIN, START)
        ac(EVENT_ID, EVENT_EXTRA)
        doorpi.DoorPi().keyboard.output.assert_called_once_with(PIN, START)

    @patch('threading.Event')
    @patch('doorpi.DoorPi', DoorPi)
    def test_triggered(self, event):
        ac = action.instantiate(PIN, START, STOP, HOLD)
        ac(EVENT_ID, EVENT_EXTRA)

        o = doorpi.DoorPi().keyboard.output
        self.assertEqual(o.call_count, 2)
        self.assertEqual(o.call_args_list, [((PIN, START),), ((PIN, STOP),)])
        event.return_value.clear.assert_called_once_with()
        event.return_value.wait.assert_called_once_with(timeout=HOLD)
        event.return_value.set.assert_not_called()
