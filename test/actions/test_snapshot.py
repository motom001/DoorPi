from pathlib import Path
from unittest.mock import patch

from doorpi.actions import snapshot

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase


class TestURLSnapshotAction(DoorPiTestCase):

    @patch("requests.get")
    @patch("doorpi.DoorPi", DoorPi)
    def test_action(self, get):
        snap_path = Path.cwd() / "snapshots"
        snap_path.mkdir()
        Path("doorpi.ini").write_text(f"[DoorPi]\nsnapshot_path = {snap_path}")

        ac = snapshot.URLSnapshotAction("http://localhost")
        ac(EVENT_ID, EVENT_EXTRA)
        get.assert_called_once_with("http://localhost", stream=True)

    @patch("doorpi.DoorPi", DoorPi)
    def test_cleanup(self):
        snap_path = Path.cwd() / "snapshots"
        snap_path.mkdir()
        Path("doorpi.ini").write_text(f"[DoorPi]\nsnapshot_path = {snap_path}\nsnapshot_keep = 10")
        for i in range(60):
            (snap_path / f"1970-01-01 00:{i:02d}:00.jpg").open("w").close()

        with self.assertLogs("doorpi.actions.snapshot", "INFO"):
            snapshot.SnapshotAction.cleanup()

        expected_files = [f"1970-01-01 00:{i:02d}:00.jpg" for i in range(50, 60)]
        actual_files = sorted(f.name for f in snap_path.iterdir())
        self.assertEqual(actual_files, expected_files)


class TestPicamSnapshotAction(DoorPiTestCase):

    def setUp(self):
        try:
            import picamera  # pylint: disable=import-outside-toplevel
        except ImportError as err:
            if err.name == "picamera":
                self.skipTest("picamera module not available")
            else: raise
        super().setUp()

    @patch('picamera.PiCamera')
    @patch('doorpi.DoorPi', DoorPi)
    def test_action(self, picamera):
        snapshot.PicamSnapshotAction()(EVENT_ID, EVENT_EXTRA)

        pcobj = picamera.return_value
        pcobj.__enter__.assert_called_once()
        cap = pcobj.__enter__.return_value.capture
        cap.assert_called_once()
