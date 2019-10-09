from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase
from unittest.mock import patch

import doorpi
import doorpi.actions.sleep as action


EVENT_ID = "ABCDEF"
EXTRA = {}


class TestActionCall(DoorPiTestCase):

    @patch('doorpi.actions.sleep.sleep')
    @patch('doorpi.DoorPi', DoorPi)
    def test_action(self, sleep):
        ac = action.instantiate("5")
        ac(EVENT_ID, EVENT_EXTRA)
        sleep.assert_called_with(5.0)

    @patch('doorpi.actions.sleep.sleep')
    @patch('doorpi.DoorPi', DoorPi)
    def test_invalid_value(self, sleep):
        with self.assertRaises(ValueError):
            action.instantiate("some string")
