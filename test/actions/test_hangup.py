from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase
from unittest.mock import patch

import doorpi
import doorpi.actions.hangup as action


EVENT_ID = "ABCDEF"
EXTRA = {}


class TestActionHangup(DoorPiTestCase):

    @patch('doorpi.DoorPi', DoorPi)
    def test_action(self):
        ac = action.instantiate()
        doorpi.DoorPi().sipphone.hangup.assert_not_called()

        ac(EVENT_ID, EVENT_EXTRA)
        doorpi.DoorPi().sipphone.hangup.assert_called_once_with()
