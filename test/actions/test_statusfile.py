import tempfile
from pathlib import Path
from unittest.mock import patch

from doorpi.actions import statusfile

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase

CONTENT = """

!BASEPATH!, some content

and some more !STUFF!

Additionally, some strange characters:
    \U0001F408 \r

"""


class TestActionStatusfile(DoorPiTestCase):

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_action(self, _):
        sf = Path.cwd() / "status.txt"
        sf.write_text("some initial garbage content")

        ac = statusfile.StatusfileAction(str(sf), CONTENT)
        self.assertEqual("", sf.read_text())

        ac(EVENT_ID, EVENT_EXTRA)
        self.assertEqual(CONTENT.strip(), sf.read_text())

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_noperm(self, _):
        with tempfile.TemporaryDirectory() as tmpdir:
            sf = Path(tmpdir, "status.txt")
            sf.open("w").close()
            sf.chmod(0)

            try:
                sf.open("r").close()
            except PermissionError:
                pass
            else:
                self.skipTest("Revoking permissions is not supported")

            with self.assertRaises(PermissionError):
                statusfile.StatusfileAction(str(sf), CONTENT)
