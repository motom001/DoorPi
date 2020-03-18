import tempfile
from pathlib import Path
from unittest.mock import patch

import doorpi.actions.statusfile as action

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase


CONTENT = """

!BASEPATH!, some content

and some more !STUFF!

Additionally, some strange characters:
    \U0001F408 \r

"""


class TestActionStatusfile(DoorPiTestCase):

    @patch('doorpi.DoorPi', DoorPi)
    def test_action(self):
        sf = Path.cwd() / "status.txt"
        sf.write_text("some initial garbage content")

        ac = action.instantiate(str(sf), CONTENT)
        self.assertEqual("", sf.read_text())

        ac(EVENT_ID, EVENT_EXTRA)
        self.assertEqual(CONTENT.strip() + "\n", sf.read_text())

    @patch('doorpi.DoorPi', DoorPi)
    def test_noperm(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sf = Path(tmpdir, "status.txt")
            sf.open("w").close()
            sf.chmod(0)

            with self.assertRaises(PermissionError):
                action.instantiate(str(sf), CONTENT)
