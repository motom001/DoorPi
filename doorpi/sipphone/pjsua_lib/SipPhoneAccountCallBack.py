#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import threading
import datetime
import time
import os
import pjsua as pj
from doorpi import DoorPi
from SipPhoneCallCallBack import SipPhoneCallCallBack as CallCallback

class SipPhoneAccountCallBack(pj.AccountCallback):

    sem = None

    def __init__(self, account = None):
        logger.debug("__init__")
        pj.AccountCallback.__init__(self, account)
        DoorPi().event_handler.register_event('BeforeCallIncoming', __name__)
        DoorPi().event_handler.register_event('OnCallReconnect', __name__)
        DoorPi().event_handler.register_event('AfterCallReconnect', __name__)
        DoorPi().event_handler.register_event('OnCallBusy', __name__)
        DoorPi().event_handler.register_event('AfterCallBusy', __name__)
        DoorPi().event_handler.register_event('OnCallIncoming', __name__)
        DoorPi().event_handler.register_event('AfterCallIncoming', __name__)
        DoorPi().event_handler.register_event('OnCallReject', __name__)
        DoorPi().event_handler.register_event('AfterCallReject', __name__)
        #DoorPi().event_handler.register_event('AfterAccountRegState', __name__)

    def __del__(self):
        self.destroy()

    def destroy(self):
        logger.debug("destroy")
        DoorPi().event_handler.unregister_source(__name__, True)

    def wait(self):
        self.sem = threading.Semaphore(0)
        self.sem.acquire()

    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()

        #DoorPi().event_handler('AfterAccountRegState', __name__)
        #logger.debug(self.account.info.reg_status)

    def answer_call(self, call):
        DoorPi().sipphone.current_callcallback = CallCallback()
        call.set_callback(DoorPi().sipphone.current_callcallback)
        DoorPi().sipphone.current_call = call
        DoorPi().sipphone.current_call.answer(code = 200)

    def on_incoming_call(self, call):
        # SIP-Status-Codes: http://de.wikipedia.org/wiki/SIP-Status-Codes
        # 200 = OK
        # 401 = Unauthorized
        # 403 = Forbidden
        # 486 = Busy Here
        # 494 = Security Agreement Required
        logger.debug("on_incoming_call")
        logger.info("Incoming call from %s", str(call.info().remote_uri))
        DoorPi().event_handler('BeforeCallIncoming', __name__)

        call.answer(180)

        if DoorPi().sipphone.current_call is not None and DoorPi().sipphone.current_call.is_valid():
            logger.debug("Incoming call while another call is active")
            logger.debug("- incoming.remote_uri: %s", call.info().remote_uri)
            logger.debug("- current.remote_uri : %s", DoorPi().sipphone.current_call.info().remote_uri)

            if call.info().remote_uri == DoorPi().sipphone.current_call.info().remote_uri:
                logger.info("Current call is incoming call - quitting current and connecting to incoming. Maybe connection reset?")
                DoorPi().event_handler('OnCallReconnect', __name__, {'remote_uri': call.info().remote_uri})
                DoorPi().current_call.hangup()
                self.answer_call(call)
                DoorPi().event_handler('AfterCallReconnect', __name__)
                return
            else:
                logger.info("Incoming and current call are different - sending busy signal to incoming call")
                DoorPi().event_handler('OnCallBusy', __name__, {'remote_uri': call.info().remote_uri})
                call.answer(code = 494, reason = "Security Agreement Required")
                DoorPi().event_handler('AfterCallBusy', __name__)
                return

        if DoorPi().sipphone.is_admin_number(call.info().remote_uri):
            logger.debug("Incoming call from trusted admin number %s -> autoanswer", call.info().remote_uri)
            DoorPi().event_handler('OnCallIncoming', __name__, {'remote_uri': call.info().remote_uri})
            self.answer_call(call)
            DoorPi().event_handler('AfterCallIncoming', __name__)
            return
        else:
            logger.debug("Incoming call ist not from a trusted admin number %s -> sending busy signal", call.info().remote_uri)
            DoorPi().event_handler('OnCallReject', __name__, {'remote_uri': call.info().remote_uri})
            call.answer(code = 494, reason = "Security Agreement Required")
            DoorPi().event_handler('AfterCallReject', __name__)
            return