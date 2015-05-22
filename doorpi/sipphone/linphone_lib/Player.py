#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import os

import doorpi
from media.CreateDialTone import generate_dial_tone
from sipphone.AbstractBaseClass import PlayerAbstractBaseClass

class LinphonePlayer(PlayerAbstractBaseClass):

    __player_id = None
    __slot_id = None

    __player_filename = ''

    @property
    def player_filename(self): return self.__player_filename

    def __init__(self):
        self.__player_filename = doorpi.DoorPi().config.get('DoorPi', 'dialtone', '')
        if self.__player_filename is '':
            logger.debug('no player found in config at section DoorPi and key dialtone')
            return

        doorpi.DoorPi().event_handler.register_action('OnSipPhoneDestroy', self.destroy)

        self.__player_filename = doorpi.DoorPi().parse_string(self.__player_filename)
        if not os.path.exists(os.path.dirname(self.__player_filename)):
            logger.info('Path %s not exists - create it now', os.path.dirname(self.__player_filename))
            os.makedirs(os.path.dirname(self.__player_filename))
        dialtone_renew_every_start = doorpi.DoorPi().config.get_bool('DoorPi', 'dialtone_renew_every_start', False)
        if not os.path.isfile(self.__player_filename) or dialtone_renew_every_start:
            logger.info('DialTone %s not exists - create it now', self.__player_filename)
            dialtone_volume = doorpi.DoorPi().config.get_int('DoorPi', 'dialtone_volume', 35)
            generate_dial_tone(self.__player_filename, dialtone_volume)
        doorpi.DoorPi().event_handler.register_event('OnPlayerStarted', __name__)
        doorpi.DoorPi().event_handler.register_event('OnPlayerStopped', __name__)
        doorpi.DoorPi().event_handler.register_event('OnPlayerCreated', __name__)

        doorpi.DoorPi().event_handler.register_action('OnSipPhoneMakeCall', self.start)
        doorpi.DoorPi().event_handler.register_action('OnCallStateConnect', self.stop)
        doorpi.DoorPi().event_handler.register_action('OnCallStateDisconnect', self.stop)

        doorpi.DoorPi().event_handler('OnPlayerCreated', __name__)

    def start(self): doorpi.DoorPi().event_handler('OnPlayerStarted', __name__)
    def stop(self):  doorpi.DoorPi().event_handler('OnPlayerStopped', __name__)
    def destroy(self):
        self.stop()
        doorpi.DoorPi().event_handler.unregister_source(__name__, True)
