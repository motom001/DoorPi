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
        with tempfile.NamedTemporaryFile(mode="w+") as tmpfile:
            tmpfile.write("some initial garbage content")
            tmpfile.flush()
            tmpfile.seek(0)

            ac = action.instantiate(tmpfile.name, CONTENT)
            self.assertEqual(tmpfile.read(), "")
            tmpfile.seek(0)

            ac(EVENT_ID, EVENT_EXTRA)
            self.assertEqual(tmpfile.read(), CONTENT.strip() + "\n")
            tmpfile.seek(0)

    @patch('doorpi.DoorPi', DoorPi)
    def test_noperm(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fpath = os.path.join(tmpdir, "status.txt")
            open(fpath, "w").close()
            os.chmod(fpath, mode=0)

            with self.assertRaises(PermissionError):
                action.instantiate(fpath, CONTENT)
