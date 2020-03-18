from unittest.mock import patch

import doorpi
import doorpi.actions.call as action

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase


SIPURL = "sip:null@null"


class TestActionCall(DoorPiTestCase):

    @patch('doorpi.DoorPi', DoorPi)
    def test_action(self):
        ac = action.instantiate(SIPURL)
        doorpi.DoorPi().sipphone.call.assert_not_called()

        ac(EVENT_ID, EVENT_EXTRA)
        doorpi.DoorPi().sipphone.call.assert_called_once_with(SIPURL)
