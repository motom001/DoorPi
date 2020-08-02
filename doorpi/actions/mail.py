"""Actions related to emails: mailto"""

import email.message
import logging
import smtplib

import doorpi
from . import action

LOGGER = logging.getLogger(__name__)


@action("mail")
@action("mailto")
class MailAction:
    """Sends an email with customizable subject and text, optionally with the latest snapshot."""

    def __init__(self, to, subject="Doorbell", text="Someone rang the door!", snapshot="false"):
        self.__to = str(to)
        self.__subject = str(subject)
        self.__snap = str(snapshot).lower().strip() in ["true", "yes", "on", "1"]

        cfg = doorpi.INSTANCE.config
        self.__host = cfg.get_string("SMTP", "server")
        self.__port = cfg.get_int("SMTP", "port", 0)

        need_login = cfg.get_bool("SMTP", "need_login", True)
        if need_login:
            self.__user = cfg.get_string("SMTP", "username")
            self.__pass = cfg.get_string("SMTP", "password")
        else:
            self.__user = self.__pass = None

        self.__from = cfg.get_string("SMTP", "from", f"\"DoorPi\" <{self.__user}@{self.__host}>")
        self.__ssl = cfg.get_bool("SMTP", "use_ssl", False)
        self.__starttls = cfg.get_bool("SMTP", "use_tls", True)
        self.__signature = cfg.get_string("SMTP", "signature", "!EPILOG!")  # not parsed yet

        if text.startswith("/"):
            # Read actual text from file
            self.__textfile = text
            with open(text, "rt") as textfile:
                self.__text = textfile.read()
        else:
            self.__textfile = None
            self.__text = text

        if not self.__host: raise ValueError("No SMTP host set")
        if self.__port < 0 or self.__port > 65535: raise ValueError("Invalid SMTP port")
        if need_login and not self.__user:
            raise ValueError("need_login = True, but no SMTP user specified")
        if self.__ssl and self.__starttls: raise ValueError("Cannot combine SSL and STARTTLS")

        # Test the SMTP connection by greeting the server and logging in
        with smtplib.SMTP_SSL(self.__host, self.__port) if self.__ssl \
                else smtplib.SMTP(self.__host, self.__port) as smtp:
            self._start_session(smtp)

    def __call__(self, event_id, extra):
        msg = email.message.EmailMessage()
        msg["From"] = self.__from
        msg["To"] = self.__to
        msg["Subject"] = doorpi.INSTANCE.parse_string(self.__subject)

        text = self.__text
        if self.__signature: text += f"\n\n{self.__signature}"
        msg.set_content(doorpi.INSTANCE.parse_string(text))

        if self.__snap:
            snapfile = doorpi.INSTANCE.config.get_path("DoorPi", "last_snapshot")
            if snapfile:
                try:
                    snap_data = snapfile.read_bytes()
                    msg.add_attachment(snap_data, "application", "octet-stream", cte="base64",
                                       disposition="attachment",
                                       filename=snapfile.name)
                except Exception:  # pylint: disable=broad-except
                    LOGGER.exception("[%s] Cannot attach snapshot to email", event_id)

        with smtplib.SMTP_SSL(self.__host, self.__port) if self.__ssl \
                else smtplib.SMTP(self.__host, self.__port) as smtp:
            self._start_session(smtp)
            retval = smtp.send_message(msg)

        if retval[0] >= 400:
            LOGGER.error("[%s] Failed sending email to %s: %d %s",
                         event_id, self.__to, retval[0], retval[1].decode("utf-8"))
        else:
            LOGGER.info("[%s] Sent email to %s: %d %s",
                        event_id, self.__to, retval[0], retval[1].decode("utf-8"))

    def _start_session(self, smtp):
        if self.__starttls:
            smtp.starttls()
        if self.__user:
            smtp.login(self.__user, self.__pass)

    def __str__(self):
        return f"Send a mail to {self.__to}"

    def __repr__(self):
        return f"mailto:{self.__to},{self.__subject}," \
            f"{self.__textfile if self.__textfile is not None else self.__text}," \
            f"{self.__snap}"
