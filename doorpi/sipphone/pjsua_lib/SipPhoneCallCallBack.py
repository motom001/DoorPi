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

class SipPhoneCallCallBack(pj.CallCallback):

    cb_openDoor = None
    PlayerID = None
    Lib = None

    inAction = False

    __DTMF = ''

    def __init__(self, PlayerID = None, call = None):
        logger.debug("__init__")
        self.cb_openDoor = DoorPi()
        self.PlayerID = PlayerID
        self.Lib = pj.Lib.instance()
        pj.CallCallback.__init__(self, call)

    def __del__(self):
        self.destroy()

    def destroy(self):
        logger.debug("destroy")

    def on_media_state(self):
        logger.debug("on_media_state (%s)",str(self.call.info().media_state))

    def on_state(self):
        logger.debug("on_state (%s)", self.call.info().state_text)

        if self.inAction is not False:
            logger.debug("wait for finished action '%s'", self.inAction)
            while self.inAction is not False: time.sleep(0.1)
            logger.debug("action finished '%s'", self.inAction)

        if self.call.info().state in [pj.CallState.CONNECTING, pj.CallState.CONFIRMED] \
        and self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
            if self.PlayerID is not None:
                self.Lib.conf_disconnect(self.Lib.player_get_slot(self.PlayerID), 0)
            self.Lib.conf_connect(call_slot, 0)
            self.Lib.conf_connect(0, call_slot)
            logger.debug("conneted Media to call_slot %s",str(call_slot))

        if self.call.info().state == pj.CallState.DISCONNECTED:
            call_slot = self.call.info().conf_slot
            self.Lib.conf_disconnect(call_slot, 0)
            self.Lib.conf_disconnect(0, call_slot)
            logger.debug("disconneted Media from call_slot %s",str(call_slot))

    def on_dtmf_digit(self, digits):
        logger.debug("on_dtmf_digit: %s",str(digits))
        self.__DTMF += str(digits)

        possible_DTMF = DoorPi().get_config().get_keys('DTMF')

        for DTMF in possible_DTMF:
            if self.__DTMF.endswith(DTMF[1:-1]):
                self.inAction = DoorPi().get_config().get('DTMF', DTMF)
                logger.debug("on_dtmf_digit: get DTMF-request (%s) for action %s", DTMF, self.inAction)
                DoorPi().fire_action(self.inAction)
                self.inAction = False


