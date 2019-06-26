"""This module contains the "glue class", which binds PJSUA2 to DoorPi."""

import pjsua2 as pj
import threading

from doorpi import DoorPi
from doorpi.sipphone.abc import AbstractSIPPhone

from . import EVENT_SOURCE, fire_event, logger
from .config import Config
from .worker import Worker


class Pjsua2(AbstractSIPPhone):

    def get_name(self): return "pjsua2"

    def __init__(self):
        eh = DoorPi().event_handler
        for ev in [
                # Fired by this class
                "OnSIPPhoneCreate", "OnSIPPhoneStart", "OnSIPPhoneDestroy",
                "OnCallOutgoing", "OnCallOutgoing_S",
                # Fired by AccountCallback
                "BeforeCallIncoming", "OnCallIncoming", "OnCallBusy", "OnCallReject",
                "BeforeCallIncoming_S", "OnCallIncoming_S", "OnCallBusy_S", "OnCallReject_S",
                # Fired by CallCallback (all) and Worker (disconnect)
                "OnCallConnect", "OnCallDisconnect",
                "OnCallConnect_S", "OnCallDisconnect_S",
        ]:
            eh.register_event(ev, EVENT_SOURCE)

        # register DTMF events, fired by CallCallback
        for dtmf in DoorPi().config.get_keys("DTMF"):
            eh.register_event(f"OnDTMF_{dtmf}", EVENT_SOURCE)

        self.__ep = None

        self.__waiting_calls = []  # outgoing calls that are not yet connected
        self.__ringing_calls = []  # outgoing calls that are currently ringing
        self.__call_lock = threading.Lock()
        self.current_call = None

        # Python doesn't like being called from native threads, so we
        # need our own worker.
        self.__worker = None
        self.__worker_thread = None
        fire_event("OnSIPPhoneCreate", async_only=True)
        eh.register_action("OnShutdown", self.__del__)

    def __del__(self):
        logger.debug("Destroying PJSUA2 SIP phone")
        fire_event("OnSIPPhoneDestroy", async_only=True)

        with self.__call_lock:
            if self.__worker is not None:
                self.__worker.running = False
                self.__worker_thread.join()
            del self.__worker_thread
            del self.__worker
        DoorPi().event_handler.unregister_source(EVENT_SOURCE, True)

    def start(self):
        logger.info("Starting PJSUA2 SIP phone")
        logger.trace("Starting worker thread")
        self.__worker = Worker(self)
        self.__worker_thread = threading.Thread(target=self.__worker)
        self.__worker_thread.name = "pjworker"
        self.__worker_thread.start()
        self.__worker.ready.acquire()  # wait for thread startup

        if self.__worker.error is not None:
            self.__worker_thread.join()
            raise RuntimeError("PJSUA2 initialization failed") from self.__worker.error

        self.__ep = pj.Endpoint.instance()

        fire_event("OnSIPPhoneStart", async_only=True)
        logger.info("Start successful")

    def self_check(self):
        if self.__worker is None:
            raise RuntimeError("self_check() called, but PJSUA2 module was not start()ed yet")
        if self.__worker.error is not None:
            raise RuntimeError("PJSUA2 python worker died") from self.__worker.error

    def call(self, uri):
        try: canonical_uri = self.canonicalize_uri(uri)
        except ValueError: return False
        logger.trace("About to call %s (canonicalized: %s)", uri, canonical_uri)

        with self.__call_lock:
            if self.current_call is not None:
                # Another call is already active
                return False
            if canonical_uri in self.__waiting_calls \
                + [c.getInfo().remoteUri for c in self.__ringing_calls]:
                return False

            # Dispatch creation of the call to the worker thread. This
            # prevents PJSIP from permanently allocating memory to
            # track short lived event threads.
            self.__waiting_calls += [canonical_uri]
            with self.__worker.wake:
                self.__worker.wake.notify()
            return True

    def dump_call(self) -> dict:
        logger.trace("Dumping current call info")

        c = self.current_call
        if c is not None:
            ci = c.getInfo()
            return {
                "direction": "outgoing" if ci.role == pj.PJSIP_ROLE_UAC else "incoming",
                "remote_uri": ci.remoteUri,
                "total_time": ci.connectDuration,
                "camera": False
            }
        return {}

    def hangup(self) -> None:
        logger.trace("Hanging up all calls")
        with self.__call_lock:
            self.__worker.hangup += 1
        with self.__worker.wake:
            self.__worker.wake.notify()
        self.__worker.ready.wait()

    def is_admin(self, uri: str) -> bool:
        try: canonical_uri = self.canonicalize_uri(uri)
        except ValueError: return False

        conf = DoorPi().config
        section = "SIP-Admin"
        for admin_number in conf.get_keys(section):
            if admin_number == "*":
                logger.trace("Found '*' in config: everything is an admin number")
                return True
            elif canonical_uri == self.canonicalize_uri(admin_number) \
                and conf.get_string(section, admin_number) == "active":
                logger.trace("%s is admin number %s", uri, admin_number)
                return True
        logger.trace("%s is not an admin number", uri)
        return False

    def canonicalize_uri(self, uri: str) -> str:
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
            canonical_uri = canonical_uri + "@" + Config.sipphone_server()
        logger.trace("Canonicalized URI '%s' as '%s'", uri, canonical_uri)

        uri_status = self.__ep.utilVerifySipUri(canonical_uri)
        if uri_status != pj.PJ_SUCCESS:
            msg = f"Unable to form a valid URI from {uri}"
            logger.error(msg)
            raise ValueError(msg)
        return canonical_uri
