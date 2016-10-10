#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import os

from doorpi import DoorPi
from doorpi.sipphone.AbstractBaseClass import RecorderAbstractBaseClass

class PjsuaRecorder(RecorderAbstractBaseClass):

    __rec_id = None
    __slot_id = None

    __record_filename = ''
    __last_record_filename = ''

    @property
    def record_filename(self): return self.__record_filename

    @property
    def parsed_record_filename(self): return DoorPi().parse_string(self.__record_filename)

    @property
    def last_record_filename(self): return self.__last_record_filename

    def __init__(self):
        self.__record_filename = DoorPi().config.get('DoorPi', 'records',
                                                     '!BASEPATH!/records/%Y-%m-%d_%H-%M-%S.wav')
        if self.__record_filename is '':
            logger.debug('no recorder found in config at section DoorPi and key records')
            return

        DoorPi().event_handler.register_event('OnRecorderStarted', __name__)
        DoorPi().event_handler.register_event('OnRecorderStopped', __name__)
        DoorPi().event_handler.register_event('OnRecorderCreated', __name__)

        if DoorPi().config.get_bool('DoorPi', 'record_while_dialing', 'False') is True:
            DoorPi().event_handler.register_action('OnSipPhoneMakeCall', self.start)
        else:
            DoorPi().event_handler.register_action('OnCallStateConnect', self.start)

        DoorPi().event_handler.register_action('OnCallStateDisconnect', self.stop)

        DoorPi().event_handler('OnRecorderCreated', __name__)

    def start(self):
        if self.__record_filename is '':
            return

        if self.__rec_id is not None:
            logger.trace('recorder already created as rec_id %s and record to %s', self.__rec_id, self.last_record_filename)
            return

        DoorPi().sipphone.lib.thread_register('PjsuaPlayer_start_thread')

        if self.__record_filename is not '':
            self.__last_record_filename = DoorPi().parse_string(self.__record_filename)
            if not os.path.exists(os.path.dirname(self.__last_record_filename)):
                logger.info('Path %s not exists - create it now', os.path.dirname(self.__last_record_filename))
                os.makedirs(os.path.dirname(self.__last_record_filename))

            logger.debug('starting recording to %s', self.__last_record_filename)
            self.__rec_id = DoorPi().sipphone.lib.create_recorder(self.__last_record_filename)
            self.__slot_id = DoorPi().sipphone.lib.recorder_get_slot(self.__rec_id)
            DoorPi().sipphone.lib.conf_connect(0, self.__slot_id)
            DoorPi().event_handler('OnRecorderStarted', __name__)

    def stop(self):
        if self.__rec_id is not None:
            DoorPi().sipphone.lib.thread_register('PjsuaPlayer_start_thread')
            logger.debug('stopping recording to %s', self.__last_record_filename)
            DoorPi().sipphone.lib.conf_disconnect(0, self.__slot_id)
            DoorPi().sipphone.lib.recorder_destroy(self.__rec_id)
            self.__rec_id = None
            self.__slot_id = None
            DoorPi().event_handler('OnRecorderStopped', __name__)