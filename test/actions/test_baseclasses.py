from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase
from unittest.mock import MagicMock, patch

import doorpi


class TestActionInstantiation(DoorPiTestCase):

    @patch("doorpi.actions.log.instantiate")
    def test_nocolon(self, m):
        doorpi.actions.from_string("log")
        m.assert_called_once_with()

    @patch("doorpi.actions.log.instantiate")
    def test_colon(self, m):
        doorpi.actions.from_string("log:")
        m.assert_called_once_with()

    @patch("doorpi.actions.log.instantiate")
    def test_args(self, m):
        doorpi.actions.from_string("log:foo,bar,baz")
        m.assert_called_once_with("foo", "bar", "baz")

    def test_emptystring(self):
        ac = doorpi.actions.from_string("")
        self.assertIsNone(ac)

    def test_underscore(self):
        with self.assertRaises(ValueError):
            doorpi.actions.from_string("_test")


class TestCallbackAction(DoorPiTestCase):

    def test_callback(self):
        m = MagicMock()
        ac = doorpi.actions.CallbackAction(
            m, "some arg", kw="some keyword arg", args=["foo", "bar"])
        ac(EVENT_ID, EVENT_EXTRA)
        m.assert_called_once_with("some arg", kw="some keyword arg", args=["foo", "bar"])

    def test_callback_uncallable(self):
        with self.assertRaises(ValueError):
            doorpi.actions.CallbackAction(None)


class TestCheckAction(DoorPiTestCase):

    def test_check_passing(self):
        m = MagicMock()
        ac = doorpi.actions.CheckAction(m)
        ac(EVENT_ID, EVENT_EXTRA)
        m.assert_called_with()

    @patch("doorpi.DoorPi", DoorPi)
    def test_check_failing(self):
        m = MagicMock(side_effect=Exception)
        ac = doorpi.actions.CheckAction(m)

        with self.assertLogs("doorpi.actions", "ERROR"):
            ac(EVENT_ID, EVENT_EXTRA)
        DoorPi().doorpi_shutdown.assert_called_once_with()
