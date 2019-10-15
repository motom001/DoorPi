from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase
from unittest.mock import patch

import os
import os.path
import tempfile

import doorpi
import doorpi.actions.statusfile as action


CONTENT = """

!BASEPATH!, some content

and some more !STUFF!

Additionally, some strange characters:
    \U0001F408 \r

"""


class TestActionStatusfile(DoorPiTestCase):

    @patch('doorpi.DoorPi', DoorPi)
    def test_action(self):
        with open("status.txt", "w") as f:
            f.write("some initial garbage content")

        ac = action.instantiate(os.path.join(os.getcwd(), "status.txt"), CONTENT)
        with open("status.txt", "r") as f:
            self.assertEqual(f.read(), "")

        ac(EVENT_ID, EVENT_EXTRA)
        with open("status.txt", "r") as f:
            self.assertEqual(f.read(), CONTENT.strip() + "\n")

    @patch('doorpi.DoorPi', DoorPi)
    def test_noperm(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fpath = os.path.join(tmpdir, "status.txt")
            open(fpath, "w").close()
            os.chmod(fpath, mode=0)

            with self.assertRaises(PermissionError):
                action.instantiate(fpath, CONTENT)
