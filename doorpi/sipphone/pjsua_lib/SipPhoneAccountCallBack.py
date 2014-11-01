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
        logger.debug("on_incoming_call")
        logger.debug("Incoming call from %s", str(call.info().remote_uri))
        # TODO: -> configfile
        if call.info().remote_uri.startswith("506411"):
            logger.debug("Incoming Call from trusted number %s -> autoanswer", call.info().remote_uri)
            call.answer(200)
        else:
            call.answer(486, "Busy")
            return