from pathlib import Path
from unittest.mock import patch

from doorpi.actions import snapshot

from ..mocks import DoorPi, DoorPiTestCase
from . import EVENT_EXTRA, EVENT_ID

CONFIG = """\
[DoorPi]
snapshot_path = {}
snapshot_keep = 10
"""


class SnapshotTestCase(DoorPiTestCase):
    def setUp(self):
        super().setUp()
        self.snap_path = Path.cwd() / "snapshots"
        self.snap_path.mkdir()
        Path("doorpi.ini").write_text(CONFIG.format(self.snap_path))


class TestURLSnapshotAction(SnapshotTestCase):
    @patch("requests.get")
    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_action(self, _, get):
        ac = snapshot.URLSnapshotAction("http://localhost")
        ac(EVENT_ID, EVENT_EXTRA)
        get.assert_called_once_with("http://localhost", stream=True)

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_cleanup(self, _):
        for i in range(60):
            (self.snap_path / f"1970-01-01 00:{i:02d}:00.jpg").open(
                "w"
            ).close()

        with self.assertLogs("doorpi.actions.snapshot", "INFO"):
            snapshot.SnapshotAction.cleanup()

        expected_files = [
            f"1970-01-01 00:{i:02d}:00.jpg" for i in range(50, 60)
        ]
        actual_files = sorted(f.name for f in self.snap_path.iterdir())
        self.assertEqual(actual_files, expected_files)


class TestPicamSnapshotAction(SnapshotTestCase):
    def setUp(self):
        # pylint: disable=import-outside-toplevel, unused-import
        try:
            import picamera
        except ImportError as err:
            if err.name == "picamera":
                self.skipTest("picamera module not available")
            else:
                raise
        super().setUp()

    @patch("picamera.PiCamera")
    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_action(self, _, picamera):
        snapshot.PicamSnapshotAction()(EVENT_ID, EVENT_EXTRA)

        pcobj = picamera.return_value
        pcobj.__enter__.assert_called_once()
        cap = pcobj.__enter__.return_value.capture
        cap.assert_called_once()
