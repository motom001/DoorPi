from unittest.mock import patch

import doorpi.actions.os_execute as action

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase


# A command that is successful (i.e. returns 0)
TEST_CMD_SUCCESS = "/bin/true"
# A command that fails (i.e. returns non-zero)
TEST_CMD_FAIL = "/bin/false"


class TestOSExecuteAction(DoorPiTestCase):

    @patch('doorpi.DoorPi', DoorPi)
    def _do_test(self, cmd, result):
        # Simulate real config handling by splitting the command at commas
        ac = action.instantiate(*cmd.split(","))

        with self.assertLogs("doorpi.actions.os_execute", "INFO") as cm:
            ac(EVENT_ID, EVENT_EXTRA)

        self.assertEqual(len(cm.records), 2)
        self.assertEqual(cm.records[0].args, (EVENT_ID, cmd))
        self.assertEqual(cm.records[1].args, (EVENT_ID, result) if result != 0 else (EVENT_ID,))

    def test_successful(self):
        self._do_test(TEST_CMD_SUCCESS, 0)

    def test_failing(self):
        self._do_test(TEST_CMD_FAIL, 1)
