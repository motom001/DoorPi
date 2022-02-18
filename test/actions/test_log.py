from unittest.mock import patch

from doorpi.actions import log

from ..mocks import DoorPi, DoorPiTestCase
from . import EVENT_EXTRA, EVENT_ID

LOGMSG = "Test log message"


class TestActionCall(DoorPiTestCase):
    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_action(self, _):
        ac = log.LogAction(LOGMSG)

        with self.assertLogs("doorpi.actions.log", "INFO") as cm:
            ac(EVENT_ID, EVENT_EXTRA)

        self.assertEqual(len(cm.records), 1)
        self.assertEqual(cm.records[0].args, (EVENT_ID, LOGMSG))
