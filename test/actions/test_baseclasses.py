from unittest.mock import MagicMock, patch

import doorpi.actions

from ..mocks import DoorPi, DoorPiTestCase
from . import EVENT_EXTRA, EVENT_ID


class TestActionInstantiation(DoorPiTestCase):
    def test_successful_instantiation(self):
        for title, ac_str, parms in (
            ("No colon", "log", []),
            ("Colon, no args", "log:", []),
            ("Colon + args", "log:foo,bar,baz", ["foo", "bar", "baz"]),
        ):
            with self.subTest(title):
                with patch("doorpi.actions.log.LogAction") as action:
                    doorpi.actions.from_string(ac_str)
                    action.assert_called_once_with(*parms)

    def test_emptystring(self):
        ac = doorpi.actions.from_string("")
        self.assertIsNone(ac)


class TestCallbackAction(DoorPiTestCase):
    def test_callback(self):
        mock = MagicMock()
        ac = doorpi.actions.CallbackAction(
            mock, "some arg", kw="some keyword arg", args=["foo", "bar"]
        )
        ac(EVENT_ID, EVENT_EXTRA)
        mock.assert_called_once_with(
            "some arg", kw="some keyword arg", args=["foo", "bar"]
        )

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
