import io
import textwrap
from pathlib import Path
from unittest.mock import patch

from doorpi.actions import mail, snapshot

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase

stub_config = """\
[snapshots]
directory = "snaps"

[mail]
server = "localhost"
need_login = true
username = "test"
password = "test"
"""


class TestMailAction(DoorPiTestCase):

    def setUp(self):
        super().setUp()

        Path("doorpi.ini").write_text(textwrap.dedent("""\
            [DoorPi]
            last_snapshot = /dev/null

            [SMTP]
            server = localhost
            port = 0
            need_login = true
            username = test
            password = test
            signature = !EPILOG!
            """))

    @patch("smtplib.SMTP")
    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_send_plain(self, instance, smtp):
        instance.config.load(io.StringIO(stub_config))
        smtp.return_value.__enter__.return_value.send_message.return_value = (
            200, b"OK")
        ac = mail.MailAction(
            "test@localhost", "Test subject", "Test body", "false")

        with self.assertLogs("doorpi.actions.mail", "INFO"):
            ac(EVENT_ID, EVENT_EXTRA)

        send = smtp.return_value.__enter__.return_value.send_message
        send.assert_called_once()

        msg = send.call_args[0][0]
        self.assertEqual(msg["From"], "DoorPi <test@localhost>")
        self.assertEqual(msg["To"], "test@localhost")
        self.assertEqual(msg["Subject"], "Test subject")
        self.assertFalse(msg.is_multipart())
        self.assertEqual(msg.get_content(), "Test body\n\n!EPILOG!\n")

    @patch("smtplib.SMTP")
    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_send_snapshot(self, instance, smtp):
        instance.config.load(io.StringIO(stub_config))
        smtp.return_value.__enter__.return_value.send_message.return_value = (
            200, b"OK")
        snapshot_file = snapshot.SnapshotAction.get_next_path()
        snapshot_file.touch()

        ac = mail.MailAction(
            "test@localhost", "Test subject", "Test body", "true")
        with self.assertLogs("doorpi.actions.mail", "INFO"):
            ac(EVENT_ID, EVENT_EXTRA)

        send = smtp.return_value.__enter__.return_value.send_message
        send.assert_called_once()

        msg = send.call_args[0][0]
        self.assertEqual(msg["From"], "DoorPi <test@localhost>")
        self.assertEqual(msg["To"], "test@localhost")
        self.assertEqual(msg["Subject"], "Test subject")
        self.assertTrue(msg.is_multipart())
        atts = list(msg.iter_attachments())
        self.assertEqual(len(atts), 1)
        att = atts[0]
        self.assertEqual(att.get_filename(), snapshot_file.name)
        self.assertEqual(att.get_content_disposition(), "attachment")
