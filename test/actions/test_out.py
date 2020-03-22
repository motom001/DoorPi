from unittest.mock import patch

from doorpi.actions import out

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase


PIN = "kb.pin"
START = 1
STOP = 0
HOLD = 5


class TestActionCall(DoorPiTestCase):

    @patch('doorpi.DoorPi', DoorPi)
    def test_argvalidation(self):
        with self.assertRaises(ValueError):
            out.instantiate(PIN, START, STOP, "invalid")

    @patch('doorpi.DoorPi', DoorPi)
    def test_normal(self):
        ac = out.instantiate(PIN, START)
        ac(EVENT_ID, EVENT_EXTRA)
        DoorPi().keyboard.output.assert_called_once_with(PIN, START)

    @patch('threading.Event')
    @patch('doorpi.DoorPi', DoorPi)
    def test_triggered(self, event):
        ac = out.instantiate(PIN, START, STOP, HOLD)
        ac(EVENT_ID, EVENT_EXTRA)

        output_method = DoorPi().keyboard.output
        self.assertEqual(output_method.call_count, 2)
        self.assertEqual(output_method.call_args_list, [((PIN, START),), ((PIN, STOP),)])
        event.return_value.clear.assert_called_once_with()
        event.return_value.wait.assert_called_once_with(timeout=HOLD)
        event.return_value.set.assert_not_called()
