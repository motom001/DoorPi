import textwrap
from pathlib import Path
from unittest.mock import patch

from doorpi.actions import mail

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase


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

    @patch('smtplib.SMTP')
    @patch('doorpi.DoorPi', DoorPi)
    def test_send_plain(self, smtp):
        smtp.return_value.__enter__.return_value.send_message.return_value = (200, b"OK")
        ac = mail.MailAction("test@localhost", "Test subject", "Test body", "false")

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

    @patch('smtplib.SMTP')
    @patch('doorpi.DoorPi', DoorPi)
    def test_send_snapshot(self, smtp):
        smtp.return_value.__enter__.return_value.send_message.return_value = (200, b"OK")
        ac = mail.MailAction("test@localhost", "Test subject", "Test body", "true")

        with self.assertLogs("doorpi.actions.mail", "INFO"):
            ac(EVENT_ID, EVENT_EXTRA)

        send = smtp.return_value.__enter__.return_value.send_message
        send.assert_called_once()

        msg = send.call_args[0][0]
        self.assertEqual(msg["From"], "DoorPi <test@localhost>")
        self.assertEqual(msg["To"], "test@localhost")
        self.assertEqual(msg["Subject"], "Test subject")
        self.assertTrue(msg.is_multipart())
        atts = [msg.iter_attachments()]
        self.assertEqual(len(atts), 1)
        att = next(atts[0])
        self.assertEqual(att.get_filename(), "null")
        self.assertEqual(att.get_content_disposition(), "attachment")
