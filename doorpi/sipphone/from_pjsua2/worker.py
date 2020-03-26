"""The Worker class."""
# pylint: disable=protected-access, invalid-name

import logging
import pjsua2 as pj

from doorpi import DoorPi
from doorpi.actions import CheckAction
from doorpi.sipphone import SIPPHONE_SECTION

from . import EVENT_SOURCE, config, fire_event
from .callbacks import AccountCallback, CallCallback
from .fileio import DialTonePlayer, CallRecorder

LOGGER = logging.getLogger(__name__)


class Worker():
    """Responsible for keeping everything running and performing housekeeping tasks."""

    def __init__(self, sipphone):
        self.__phone = sipphone
        self.__ep = None
        self.__account = None

        conf = DoorPi().config
        self.__call_timeout = conf.get_int(SIPPHONE_SECTION, "call_timeout", 15)
        self.__max_call_time = conf.get_int(SIPPHONE_SECTION, "max_call_time", 120)

        self.hangup = False

    def shutdown(self):
        """Destroys the native library."""
        DoorPi().event_handler.fire_event_sync("OnSIPPhoneDestroy", EVENT_SOURCE)
        self.__ep.libDestroy()

    def setup(self):
        """Initializes the native library."""
        LOGGER.info("Initializing native library")
        self.__ep = pj.Endpoint()
        # N.B.: from PJSIP's perspective, the thread that calls
        # libCreate() is the main thread. Combined with
        # ``uaConfig.mainThreadOnly``, this ensures that all PJSIP
        # events will be handled here, and not by any native threads.
        self.__ep.libCreate()
        self.__ep.libInit(config.endpoint_config())
        self.__ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, config.transport_config())
        config.setup_audio(self.__ep)
        self.__ep.libStart()

        LOGGER.debug("Creating account")
        self.__account = AccountCallback()
        self.__account.create(config.account_config())

        self.__phone.dialtone = DialTonePlayer(**config.dialtone_config())
        self.__phone.recorder = CallRecorder(**config.recorder_config())

        # Make sure the library can fully start up
        while True:
            num_ev = self.__ep.libHandleEvents(20)  # note: libHandleEvents() takes milliseconds
            if num_ev == 0: break
            if num_ev < 0:
                raise RuntimeError("Error while initializing PJSUA2: {msg} ({errno})"
                                   .format(errno=-num_ev, msg=self.__ep.utilStrError(-num_ev)))

        # register tick actions
        eh = DoorPi().event_handler
        eh.register_action("OnTimeRapidTick", CheckAction(self.handleNativeEvents))
        eh.register_action("OnTimeTick", CheckAction(self.checkHangupAll))
        eh.register_action("OnTimeTick", CheckAction(self.checkCallTime))
        eh.register_action("OnTimeRapidTick", CheckAction(self.createCalls))
        eh.fire_event_sync("OnSIPPhoneStart", EVENT_SOURCE)
        LOGGER.debug("Initialization complete")

    def handleNativeEvents(self):
        """Polls events from the native library."""
        num_ev = self.__ep.libHandleEvents(0)
        if num_ev < 0:
            raise RuntimeError("Error while handling PJSUA2 native events: {msg} ({errno})"
                               .format(errno=-num_ev, msg=self.__ep.utilStrError(-num_ev)))

    def checkHangupAll(self):
        """Check if hanging up all calls was requested"""

        if not self.hangup: return

        with self.__phone._Pjsua2__call_lock:
            prm = pj.CallOpParam()
            self.__phone._Pjsua2__waiting_calls = []

            for call in self.__phone._Pjsua2__ringing_calls:
                try:
                    call.hangup(prm)
                except pj.Error as err:
                    if err.reason.endswith("(PJSIP_ESESSIONTERMINATED)"): continue
                    LOGGER.exception("Error hanging up a call: %s (ignored)", err.reason)
            self.__phone._Pjsua2__ringing_calls = []

            if self.__phone.current_call is not None:
                self.__phone.current_call.hangup(prm)
            else:
                # Synthesize a disconnect event
                fire_event("OnCallDisconnect", remote_uri="sip:null@null")
            self.hangup = False

    def checkCallTime(self):
        """Check all current calls and enforce call time restrictions"""

        if self.__phone.current_call is None and len(self.__phone._Pjsua2__ringing_calls) == 0:
            return

        with self.__phone._Pjsua2__call_lock:
            call = self.__phone.current_call
            if call is not None:
                ci = call.getInfo()
                if self.__max_call_time > 0 \
                        and ci.state == pj.PJSIP_INV_STATE_CONFIRMED \
                        and ci.connectDuration.sec >= self.__max_call_time:
                    LOGGER.info("Hanging up call to %s after %d seconds",
                                repr(ci.remoteUri), self.__max_call_time)
                    fire_event("OnCallTimeExceeded")
                    prm = pj.CallOpParam()
                    call.hangup(prm)
                    self.__phone.current_call = None
            else:
                synthetic_disconnect = False
                prm = pj.CallOpParam()
                for call in self.__phone._Pjsua2__ringing_calls:
                    try:
                        ci = call.getInfo()
                        if ci.totalDuration.sec >= self.__call_timeout:
                            LOGGER.info("Call to %s unanswered after %d seconds, giving up",
                                        repr(ci.remoteUri), self.__call_timeout)
                            call.hangup(prm)
                            self.__phone._Pjsua2__ringing_calls.remove(call)
                            synthetic_disconnect = True
                    except pj.Error as err:
                        if err.reason.endswith("(PJSIP_ESESSIONTERMINATED)"):
                            LOGGER.warning("Found a call that was already dead, removing it")
                        else:
                            LOGGER.exception("Can't get info for a call: %s", err.reason)
                        self.__phone._Pjsua2__ringing_calls.remove(call)
                if synthetic_disconnect and len(self.__phone._Pjsua2__ringing_calls) == 0:
                    # Last ringing call was cancelled
                    fire_event("OnCallUnanswered")

    def createCalls(self):
        """Create requested outbound calls"""
        if len(self.__phone._Pjsua2__waiting_calls) == 0:
            return

        with self.__phone._Pjsua2__call_lock:
            for uri in self.__phone._Pjsua2__waiting_calls:
                LOGGER.info("Calling %s", uri)
                fire_event("OnCallOutgoing", remote_uri=uri)
                call = CallCallback(self.__account)
                callprm = pj.CallOpParam(True)
                try:
                    call.makeCall(uri, callprm)
                except pj.Error as err:
                    LOGGER.error("Error making a call: %s", err.info())
                self.__phone._Pjsua2__ringing_calls += [call]
            self.__phone._Pjsua2__waiting_calls = []
