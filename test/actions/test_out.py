from unittest.mock import patch

from doorpi.actions import out

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase


PIN = "kb.pin"
START = 1
STOP = 0
HOLD = 5


class TestActionCall(DoorPiTestCase):

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_argvalidation(self, _):
        with self.assertRaises(ValueError):
            out.instantiate(PIN, START, STOP, "invalid")

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_normal(self, instance):
        ac = out.instantiate(PIN, START)
        ac(EVENT_ID, EVENT_EXTRA)
        instance.keyboard.output.assert_called_once_with(PIN, START)

    @patch("threading.Event")
    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_triggered(self, instance, event):
        ac = out.instantiate(PIN, START, STOP, HOLD)
        ac(EVENT_ID, EVENT_EXTRA)

        output_method = instance.keyboard.output
        self.assertEqual(output_method.call_count, 2)
        self.assertEqual(output_method.call_args_list, [((PIN, START),), ((PIN, STOP),)])
        event.return_value.clear.assert_called_once_with()
        event.return_value.wait.assert_called_once_with(timeout=HOLD)
        event.return_value.set.assert_not_called()
