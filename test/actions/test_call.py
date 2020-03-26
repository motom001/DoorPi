from tempfile import NamedTemporaryFile
from unittest.mock import patch

from doorpi.actions import call

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase


SIPURL = "sip:null@null"


class TestActionCall(DoorPiTestCase):

    @patch("doorpi.DoorPi", DoorPi)
    def test_action(self):
        ac = call.CallAction(SIPURL)
        DoorPi().sipphone.call.assert_not_called()

        ac(EVENT_ID, EVENT_EXTRA)
        DoorPi().sipphone.call.assert_called_once_with(SIPURL)


class TestActionFileCallValue(DoorPiTestCase):

    @patch("doorpi.DoorPi", DoorPi)
    def test_instantiation(self):
        with NamedTemporaryFile(mode="w") as tmpfile:
            tmpfile.write(SIPURL)

            call.CallFromFileAction(tmpfile.name)
            DoorPi().sipphone.call.assert_not_called()

    @patch("doorpi.DoorPi", DoorPi)
    def test_action(self):
        with NamedTemporaryFile(mode="w") as tmpfile:
            tmpfile.write(SIPURL)
            tmpfile.flush()

            ac = call.CallFromFileAction(tmpfile.name)
            ac(EVENT_ID, EVENT_EXTRA)
            DoorPi().sipphone.call.assert_called_once_with(SIPURL)

    @patch("doorpi.DoorPi", DoorPi)
    def test_emptyfile(self):
        with NamedTemporaryFile(mode="w") as tmpfile:
            ac = call.CallFromFileAction(tmpfile.name)
            with self.assertRaises(ValueError):
                ac(EVENT_ID, EVENT_EXTRA)


class TestActionHangup(DoorPiTestCase):

    @patch("doorpi.DoorPi", DoorPi)
    def test_action(self):
        ac = call.HangupAction()
        DoorPi().sipphone.hangup.assert_not_called()

        ac(EVENT_ID, EVENT_EXTRA)
        DoorPi().sipphone.hangup.assert_called_once_with()
