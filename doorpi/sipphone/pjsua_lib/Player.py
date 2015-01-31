#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import doorpi

class PjsuaPlayer:

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

        self.__player_filename = doorpi.DoorPi().parse_string(self.__player_filename)

        doorpi.DoorPi().event_handler.register_event('OnPlayerStarted', __name__)
        doorpi.DoorPi().event_handler.register_event('OnPlayerStopped', __name__)
        doorpi.DoorPi().event_handler.register_event('OnPlayerCreated', __name__)

        doorpi.DoorPi().event_handler.register_action('OnSipPhoneMakeCall', self.start)
        doorpi.DoorPi().event_handler.register_action('OnCallStateConnect', self.stop)

        doorpi.DoorPi().event_handler('OnPlayerCreated', __name__)

    def start(self):
        if self.__player_id is not None:
            logger.trace('player allready created as player_id %s and play %s', self.__player_id, self.player_filename)
            return

        doorpi.DoorPi().sipphone.lib.thread_register('PjsuaPlayer_start_thread')

        self.__player_filename = doorpi.DoorPi().parse_string(self.__player_filename)
        logger.debug('start player from %s', self.__player_filename)
        self.__player_id = doorpi.DoorPi().sipphone.lib.create_player(self.__player_filename, True)
        doorpi.DoorPi().sipphone.lib.player_set_pos(self.__player_id, 0)
        self.__slot_id = doorpi.DoorPi().sipphone.lib.player_get_slot(self.__player_id)
        doorpi.DoorPi().sipphone.lib.conf_connect(self.__slot_id, 0)
        doorpi.DoorPi().event_handler('OnPlayerStarted', __name__)

    def stop(self):
        if self.__player_id is not None:
            doorpi.DoorPi().sipphone.lib.thread_register('PjsuaPlayer_stop_thread')
            logger.debug('stop player from %s', self.__player_filename)
            doorpi.DoorPi().sipphone.lib.conf_disconnect(0, self.__slot_id)
            doorpi.DoorPi().sipphone.lib.player_destroy(self.__player_id)
            self.__player_id = None
            self.__slot_id = None
            doorpi.DoorPi().event_handler('OnPlayerStopped', __name__)