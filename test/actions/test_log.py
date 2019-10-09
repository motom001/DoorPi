from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase
from unittest.mock import patch

import doorpi
import doorpi.actions.log as action


EVENT_ID = "ABCDEF"
EXTRA = {}

LOGMSG = "Test log message"


class TestActionCall(DoorPiTestCase):

    @patch('doorpi.DoorPi', DoorPi)
    def test_action(self):
        ac = action.instantiate(LOGMSG)

        with self.assertLogs("doorpi.actions.log", "INFO") as cm:
            ac(EVENT_ID, EVENT_EXTRA)

        self.assertEqual(len(cm.records), 1)
        self.assertEqual(cm.records[0].args, (EVENT_ID, LOGMSG))
