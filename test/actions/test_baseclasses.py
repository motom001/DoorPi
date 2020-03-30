from unittest.mock import MagicMock, patch

import doorpi.actions

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase


class TestActionInstantiation(DoorPiTestCase):

    @patch("doorpi.actions.ACTION_REGISTRY")
    def test_nocolon(self, registry):
        registry.__contains__.return_value = True
        doorpi.actions.from_string("log")
        registry.__getitem__.assert_called_once_with("log")
        registry.__getitem__.return_value.assert_called_once_with()

    @patch("doorpi.actions.ACTION_REGISTRY")
    def test_colon(self, registry):
        registry.__contains__.return_value = True
        doorpi.actions.from_string("log:")
        registry.__getitem__.assert_called_once_with("log")
        registry.__getitem__.return_value.assert_called_once_with()

    @patch("doorpi.actions.ACTION_REGISTRY")
    def test_args(self, registry):
        registry.__contains__.return_value = True
        doorpi.actions.from_string("log:foo,bar,baz")
        registry.__getitem__.assert_called_once_with("log")
        registry.__getitem__.return_value.assert_called_once_with("foo", "bar", "baz")

    def test_emptystring(self):
        ac = doorpi.actions.from_string("")
        self.assertIsNone(ac)


class TestCallbackAction(DoorPiTestCase):

    def test_callback(self):
        mock = MagicMock()
        ac = doorpi.actions.CallbackAction(
            mock, "some arg", kw="some keyword arg", args=["foo", "bar"])
        ac(EVENT_ID, EVENT_EXTRA)
        mock.assert_called_once_with("some arg", kw="some keyword arg", args=["foo", "bar"])

    def test_callback_uncallable(self):
        with self.assertRaises(ValueError):
            doorpi.actions.CallbackAction(None)


class TestCheckAction(DoorPiTestCase):

    def test_check_passing(self):
        mock = MagicMock()
        ac = doorpi.actions.CheckAction(mock)
        ac(EVENT_ID, EVENT_EXTRA)
        mock.assert_called_with()

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_check_failing(self, instance):
        mock = MagicMock(side_effect=Exception)
        ac = doorpi.actions.CheckAction(mock)

        with self.assertLogs("doorpi.actions", "ERROR"):
            ac(EVENT_ID, EVENT_EXTRA)
        instance.doorpi_shutdown.assert_called_once_with()
