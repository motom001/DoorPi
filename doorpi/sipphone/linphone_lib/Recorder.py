#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import os

from doorpi import DoorPi
from doorpi.sipphone.AbstractBaseClass import RecorderAbstractBaseClass, SIPPHONE_SECTION

class LinphoneRecorder(RecorderAbstractBaseClass):

    __record_filename = ''
    __last_record_filename = ''

    @property
    def record_filename(self): return self.__record_filename

    @property
    def parsed_record_filename(self): return DoorPi().parse_string(self.__record_filename)

    @property
    def last_record_filename(self): return self.__last_record_filename

    def __init__(self):
        self.__record_filename = DoorPi().config.get(SIPPHONE_SECTION, 'records',
                                                     '!BASEPATH!/records/%Y-%m-%d_%H-%M-%S.wav')
        if self.__record_filename is '':
            logger.debug('no recorder found in config at section DoorPi and key records')
            return

        DoorPi().event_handler.register_action('OnSipPhoneDestroy', self.destroy)

        DoorPi().event_handler.register_event('OnRecorderStarted', __name__)
        DoorPi().event_handler.register_event('OnRecorderStopped', __name__)
        DoorPi().event_handler.register_event('OnRecorderCreated', __name__)

        if DoorPi().config.get_bool(SIPPHONE_SECTION, 'record_while_dialing', 'False') is True:
            DoorPi().event_handler.register_action('OnSipPhoneMakeCall', self.start)
        else:
            DoorPi().event_handler.register_action('OnCallStateConnect', self.start)

        DoorPi().event_handler.register_action('OnCallStateDisconnect', self.stop)

        DoorPi().event_handler('OnRecorderCreated', __name__)

    def start(self):
        if self.__record_filename is '':
            return

        if self.__record_filename is not '':
            self.__last_record_filename = self.parsed_record_filename
            if not os.path.exists(os.path.dirname(self.__last_record_filename)):
                logger.info('Path %s does not exist - creating it now', os.path.dirname(self.__last_record_filename))
                os.makedirs(os.path.dirname(self.__last_record_filename))

            logger.debug('starting recording to %s', self.__last_record_filename)
            DoorPi().sipphone.current_call.start_recording()
            DoorPi().event_handler('OnRecorderStarted', __name__, {
                'last_record_filename': self.__last_record_filename
            })

    def stop(self):
        if not DoorPi().sipphone.current_call: return
        logger.debug('stopping recording to %s', self.__last_record_filename)
        DoorPi().sipphone.current_call.stop_recording()
        DoorPi().event_handler('OnRecorderStopped', __name__, {
            'last_record_filename': self.__last_record_filename
        })

    def destroy(self):
        try: self.stop()
        except: pass
        DoorPi().event_handler.unregister_source(__name__, True)
