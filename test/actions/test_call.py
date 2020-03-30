from tempfile import NamedTemporaryFile
from unittest.mock import patch

from doorpi.actions import call

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase


SIPURL = "sip:null@null"


class TestActionCall(DoorPiTestCase):

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_action(self, instance):
        ac = call.CallAction(SIPURL)
        instance.sipphone.call.assert_not_called()

        ac(EVENT_ID, EVENT_EXTRA)
        instance.sipphone.call.assert_called_once_with(SIPURL)


class TestActionFileCallValue(DoorPiTestCase):

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_instantiation(self, instance):
        with NamedTemporaryFile(mode="w") as tmpfile:
            tmpfile.write(SIPURL)

            call.CallFromFileAction(tmpfile.name)
            instance.sipphone.call.assert_not_called()

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_action(self, instance):
        with NamedTemporaryFile(mode="w") as tmpfile:
            tmpfile.write(SIPURL)
            tmpfile.flush()

            ac = call.CallFromFileAction(tmpfile.name)
            ac(EVENT_ID, EVENT_EXTRA)
            instance.sipphone.call.assert_called_once_with(SIPURL)

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_emptyfile(self, _):
        with NamedTemporaryFile(mode="w") as tmpfile:
            ac = call.CallFromFileAction(tmpfile.name)
            with self.assertRaises(ValueError):
                ac(EVENT_ID, EVENT_EXTRA)


class TestActionHangup(DoorPiTestCase):

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_action(self, instance):
        ac = call.HangupAction()
        instance.sipphone.hangup.assert_not_called()

        ac(EVENT_ID, EVENT_EXTRA)
        instance.sipphone.hangup.assert_called_once_with()
