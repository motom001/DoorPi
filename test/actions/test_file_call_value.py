from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase
from tempfile import NamedTemporaryFile
from unittest.mock import patch
import os

import doorpi
import doorpi.actions.file_call_value as action


SIPURL = "sip:null@null"


class TestActionFileCallValue(DoorPiTestCase):

    @patch('doorpi.DoorPi', DoorPi)
    def test_instantiation(self):
        with NamedTemporaryFile(mode="w") as tmpfile:
            tmpfile.write(SIPURL)

            ac = action.instantiate(tmpfile.name)
            doorpi.DoorPi().sipphone.call.assert_not_called()

    @patch('doorpi.DoorPi', DoorPi)
    def test_action(self):
        with NamedTemporaryFile(mode="w") as tmpfile:
            tmpfile.write(SIPURL)
            tmpfile.flush()

            ac = action.instantiate(tmpfile.name)
            ac(EVENT_ID, EVENT_EXTRA)
            doorpi.DoorPi().sipphone.call.assert_called_once_with(SIPURL)

    @patch('doorpi.DoorPi', DoorPi)
    def test_emptyfile(self):
        with NamedTemporaryFile(mode="w") as tmpfile:
            ac = action.instantiate(tmpfile.name)
            with self.assertRaises(ValueError):
                ac(EVENT_ID, EVENT_EXTRA)
