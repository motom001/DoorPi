from unittest.mock import patch

import doorpi.actions.hangup as action

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase


EVENT_ID = "ABCDEF"
EXTRA = {}


class TestActionHangup(DoorPiTestCase):

    @patch('doorpi.DoorPi', DoorPi)
    def test_action(self):
        ac = action.instantiate()
        DoorPi().sipphone.hangup.assert_not_called()

        ac(EVENT_ID, EVENT_EXTRA)
        DoorPi().sipphone.hangup.assert_called_once_with()
