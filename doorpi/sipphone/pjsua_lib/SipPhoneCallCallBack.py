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

    Lib = None

    __DTMF = ''
    __possible_DTMF = []

    def __init__(self, PlayerID = None, call = None):
        logger.debug("__init__")
        self.PlayerID = PlayerID
        self.Lib = pj.Lib.instance()

        DoorPi().event_handler.register_event('OnCallMediaStateChange', __name__)
        DoorPi().event_handler.register_event('OnCallStateChange', __name__)
        DoorPi().event_handler.register_event('OnCallStateConnect', __name__)
        DoorPi().event_handler.register_event('AfterCallStateConnect', __name__)
        DoorPi().event_handler.register_event('OnCallStateDisconnect', __name__)
        DoorPi().event_handler.register_event('AfterCallStateDisconnect', __name__)
        DoorPi().event_handler.register_event('OnDTMF', __name__)

        self.__possible_DTMF = DoorPi().config.get_keys('DTMF')
        for DTMF in self.__possible_DTMF:
            DoorPi().event_handler.register_event('OnDTMF_'+DTMF, __name__)

        pj.CallCallback.__init__(self, call)

    def __del__(self):
        self.destroy()

    def destroy(self):
        logger.debug("destroy")
        DoorPi().event_handler.unregister_source(__name__, True)

    def on_media_state(self):
        logger.debug("on_media_state (%s)",str(self.call.info().media_state))
        DoorPi().event_handler('OnCallMediaStateChange', __name__, {
            'remote_uri': self.call.info().remote_uri,
            'media_state': str(self.call.info().media_state)
        })

    def on_state(self):
        logger.debug("on_state (%s)", self.call.info().state_text)
        DoorPi().event_handler('OnCallStateChange', __name__, {
            'remote_uri': self.call.info().remote_uri,
            'state': self.call.info().state_text
        })

        if self.call.info().state in [pj.CallState.CONFIRMED] \
        and self.call.info().media_state == pj.MediaState.ACTIVE:
            DoorPi().event_handler('OnCallStateConnect', __name__, {
                'remote_uri': self.call.info().remote_uri
            })
            # disconnect player with dialtone
            call_slot = self.call.info().conf_slot
            if DoorPi().sipphone.get_player_id() is not None:
                logger.trace('disconnect player')
                self.Lib.conf_disconnect(self.Lib.player_get_slot(DoorPi().sipphone.get_player_id()), 0)

            # connect to recorder
            rec_slot = DoorPi().sipphone.get_recorder_slot()
            record_while_dialing = DoorPi().sipphone.record_while_dialing
            recorder_filename = DoorPi().sipphone.parsed_recorder_filename
            if record_while_dialing is False and recorder_filename is not None:
                DoorPi().sipphone.stop_recorder_if_exists()
                rec_slot = DoorPi().sipphone.get_new_recorder_as_slot()
                self.Lib.conf_connect(0, rec_slot) # connect doorstation to recorder, if not exists
            if rec_slot is not None:
                self.Lib.conf_connect(call_slot, rec_slot) # connect phone to existing recorder

            # Connect the call to each side
            self.Lib.conf_connect(call_slot, 0)
            self.Lib.conf_connect(0, call_slot)
            logger.debug("conneted Media to call_slot %s",str(call_slot))
            DoorPi().sipphone.set_current_call(self.call)
            DoorPi().event_handler('AfterCallStateConnect', __name__, {
                'remote_uri': self.call.info().remote_uri
            })

        if self.call.info().state == pj.CallState.DISCONNECTED:
            DoorPi().event_handler('OnCallStateDisconnect', __name__, {
                'remote_uri': self.call.info().remote_uri
            })
            call_slot = self.call.info().conf_slot
            self.Lib.conf_disconnect(call_slot, 0)
            self.Lib.conf_disconnect(0, call_slot)
            DoorPi().sipphone.stop_recorder_if_exists()
            logger.debug("disconneted Media from call_slot %s",str(call_slot))
            DoorPi().sipphone.set_current_call(None)
            DoorPi().event_handler('AfterCallStateDisconnect', __name__, {
                'remote_uri': self.call.info().remote_uri
            })

    def on_dtmf_digit(self, digits):
        logger.debug("on_dtmf_digit (%s)",str(digits))

        self.__DTMF += str(digits)
        for DTMF in self.__possible_DTMF:
            if self.__DTMF.endswith(DTMF[1:-1]):
                DoorPi().event_handler('OnDTMF_'+DTMF+'', __name__, {
                    'remote_uri': self.call.info().remote_uri,
                    'DTMF': self.__DTMF
                })