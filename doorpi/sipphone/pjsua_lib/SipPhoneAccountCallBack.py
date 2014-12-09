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
import SipPhoneCallCallBack

class SipPhoneAccountCallBack(pj.AccountCallback):

    def __init__(self, account = None):
        logger.debug("__init__")
        pj.AccountCallback.__init__(self, account)

    def __del__(self):
        self.destroy()
        pj.AccountCallback.__del__(self)

    def destroy(self):
        logger.debug("destroy")

    def on_incoming_call(self, call):
        # SIP-Status-Codes: http://de.wikipedia.org/wiki/SIP-Status-Codes
        # 200 = OK
        # 401 = Unauthorized
        # 403 = Forbidden
        # 486 = Busy Here
        # 494 = Security Agreement Required
        logger.debug("on_incoming_call")
        logger.info("Incoming call from %s", str(call.info().remote_uri))
        DoorPi().fire_event('BeforeCallIncoming')

        if DoorPi().get_sipphone().get_current_call() is not None:
            logger.debug("Incoming call while another call is active")
            logger.debug("- incoming.remote_uri: %s", call.info().remote_uri)
            logger.debug("- current.remote_uri : %s", DoorPi().get_sipphone().get_current_call().info().remote_uri)

            if call.info().remote_uri == DoorPi().get_sipphone().get_current_call().info().remote_uri:
                logger.info("Current call is incoming call - quit current and connect to incoming. Maybe connection-Reset?")
                DoorPi().fire_event('OnCallReconnect', {'remote_uri': call.info().remote_uri})
                DoorPi().get_current_call().hangup()
                call.answer(code = 200)
                DoorPi().get_sipphone().set_current_call(call)
                DoorPi().get_sipphone().set_current_callback(SipPhoneCallCallBack.SipPhoneCallCallBack())
                call.set_callback(DoorPi().get_sipphone().get_current_callback())
                DoorPi().fire_event('AfterCallReconnect')
                return
            else:
                logger.info("incoming and current call are different - send busy signal to incoming call")
                DoorPi().fire_event('OnCallBusy', {'remote_uri': call.info().remote_uri})
                call.answer(code = 494, reason = "Security Agreement Required")
                DoorPi().fire_event('AfterCallBusy')
                return

        if DoorPi().get_sipphone().is_admin_number(call.info().remote_uri):
            logger.debug("Incoming Call from trusted admin number %s -> autoanswer", call.info().remote_uri)
            DoorPi().fire_event('OnCallIncomming', {'remote_uri': call.info().remote_uri})
            call.answer(code = 200)
            call.set_callback(SipPhoneCallCallBack.SipPhoneCallCallBack())
            DoorPi().get_sipphone().set_current_call(call)
            DoorPi().fire_event('AfterCallIncomming')
            return
        else:
            logger.debug("Incoming Call ist not from a trusted admin number %s -> send busy signal", call.info().remote_uri)
            DoorPi().fire_event('OnCallReject', {'remote_uri': call.info().remote_uri})
            call.answer(code = 494, reason = "Security Agreement Required")
            DoorPi().fire_event('AfterCallReject')
            return