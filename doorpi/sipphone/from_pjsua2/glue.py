"""This module contains the "glue class", which binds PJSUA2 to DoorPi."""

import logging
import threading
import pjsua2 as pj

from doorpi import DoorPi
from doorpi.actions import CallbackAction
from doorpi.sipphone.abc import AbstractSIPPhone

from . import EVENT_SOURCE, fire_event, config
from .worker import Worker

LOGGER = logging.getLogger(__name__)


class Pjsua2(AbstractSIPPhone):
    """Implements the SIP phone module interface for DoorPi."""

    def get_name(self):
        return "pjsua2"

    def __init__(self):
        super().__init__()

        eh = DoorPi().event_handler
        for ev in [
                # Fired by this class
                "OnSIPPhoneCreate",
                "OnCallOutgoing", "OnCallOutgoing_S",
                # Fired by AccountCallback
                "BeforeCallIncoming", "OnCallIncoming", "OnCallBusy", "OnCallReject",
                "BeforeCallIncoming_S", "OnCallIncoming_S", "OnCallBusy_S", "OnCallReject_S",
                # Fired by CallCallback (all) / Worker (unanswered)
                "OnCallConnect", "OnCallUnanswered",
                "OnCallConnect_S", "OnCallUnanswered_S",
                # Fired by Worker
                "OnSIPPhoneStart", "OnSIPPhoneDestroy",
                "OnCallDisconnect", "OnCallTimeExceeded",
                "OnCallDisconnect_S", "OnCallTimeExceeded_S",
        ]:
            eh.register_event(ev, EVENT_SOURCE)

        # register DTMF events, fired by CallCallback
        for dtmf in DoorPi().config.get_keys("DTMF"):
            eh.register_event(f"OnDTMF_{dtmf}", EVENT_SOURCE)

        self.__waiting_calls = []  # outgoing calls that are not yet connected
        self.__ringing_calls = []  # outgoing calls that are currently ringing
        self.__call_lock = threading.Lock()
        self.current_call = None
        self.dialtone = None

        self.__worker = None
        fire_event("OnSIPPhoneCreate", async_only=True)
        eh.register_action("OnShutdown", CallbackAction(self.__del__))

    def __del__(self):
        LOGGER.debug("Destroying PJSUA2 SIP phone")

        with self.__call_lock:
            if self.dialtone is not None:
                self.dialtone.stop()
                self.dialtone._DialTonePlayer__player = None
            self.__worker.shutdown()
            del self.__worker
        DoorPi().event_handler.unregister_source(EVENT_SOURCE, force=True)

    def start(self):
        LOGGER.info("Starting PJSUA2 SIP phone")
        LOGGER.trace("Creating worker")
        self.__worker = Worker(self)
        self.__worker.setup()
        LOGGER.info("Start successful")

    def call(self, uri):
        try:
            canonical_uri = self.canonicalize_uri(uri)
        except ValueError:
            return False
        LOGGER.trace("About to call %s (canonicalized: %s)", uri, canonical_uri)

        with self.__call_lock:
            if self.current_call is not None:
                # Another call is already active
                return False

            # Dispatch creation of the call to the main thread
            self.__waiting_calls += [canonical_uri]
            return True

    def dump_call(self) -> dict:
        LOGGER.trace("Dumping current call info")

        cc = self.current_call
        if cc is not None:
            ci = cc.getInfo()
            return {
                "direction": "outgoing" if ci.role == pj.PJSIP_ROLE_UAC else "incoming",
                "remote_uri": ci.remoteUri,
                "total_time": ci.connectDuration,
                "camera": False
            }
        return {}

    def hangup(self) -> None:
        LOGGER.trace("Hanging up all calls")
        with self.__call_lock:
            self.__worker.hangup = True

    def is_admin(self, uri: str) -> bool:
        try:
            canonical_uri = self.canonicalize_uri(uri)
        except ValueError:
            return False

        conf = DoorPi().config
        section = "SIP-Admin"
        for admin_number in conf.get_keys(section):
            if admin_number == "*":
                LOGGER.trace("Found '*' in config: everything is an admin number")
                return True
            if canonical_uri == self.canonicalize_uri(admin_number) \
                    and conf.get_string(section, admin_number) == "active":
                LOGGER.trace("%s is admin number %s", uri, admin_number)
                return True
        LOGGER.trace("%s is not an admin number", uri)
        return False

    @staticmethod
    def canonicalize_uri(uri: str) -> str:
        """Canonicalize the URI.

        Raises: ValueError if the canonicalized URI is still not valid
        Returns: The given URI, canonicalized as "sip:username@host.com"
        """

        if not uri:
            raise ValueError("Cannot canonicalize empty URI")
        canonical_uri = uri
        if canonical_uri.endswith(">"):
            # full form: "Some Name" <sip:someone@somewhere.net>
            canonical_uri = canonical_uri.split("<")[-1].split(">")[0]
        if not canonical_uri.startswith("sip:"):
            canonical_uri = "sip:" + canonical_uri
        if "@" not in canonical_uri:
            canonical_uri = f"{canonical_uri}@{config.sipphone_server()}"
        LOGGER.trace("Canonicalized URI %r as %r", uri, canonical_uri)
        return canonical_uri
