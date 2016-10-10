#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from time import sleep

logger.warning('No sipphone in config - use dummy sipphone without functionality')

import datetime

from AbstractBaseClass import SipphoneAbstractBaseClass, RecorderAbstractBaseClass, PlayerAbstractBaseClass
from doorpi import DoorPi

def get(*args, **kwargs): return DummyPhone(*args, **kwargs)
class DummyPhone(SipphoneAbstractBaseClass):

    @property
    def name(self): return 'dummy phone'

    @property
    def lib(self): return None
    @property
    def core(self): return None

    @property
    def recorder(self): return self.__recorder
    __recorder = None

    @property
    def player(self): return self.__player
    __player = None

    @property
    def current_call(self): return None

    @property
    def current_call_duration(self): return 0

    def __init__(self, whitelist = [], *args, **kwargs):
        logger.debug("__init__")
        DoorPi().event_handler.register_action('OnShutdown', self.destroy)
        DoorPi().event_handler.register_event('OnSipPhoneCreate', __name__)
        DoorPi().event_handler.register_event('OnSipPhoneStart', __name__)
        DoorPi().event_handler.register_event('OnSipPhoneDestroy', __name__)
        self.__recorder = DummyRecorder()
    def start(self):
        DoorPi().event_handler('OnSipPhoneCreate', __name__)
        DoorPi().event_handler('OnSipPhoneStart', __name__)
    def destroy(self):
        DoorPi().event_handler.fire_event_synchron('OnSipPhoneDestroy', __name__)
        DoorPi().event_handler.unregister_source(__name__, True)
    def self_check(self, *args, **kwargs):
        return
    def call(self, number):
        DoorPi().event_handler('OnSipPhoneMakeCall', __name__)
    def is_admin_number(self, remote_uri):
        return False
    def hangup(self):
        pass

class DummyRecorder(RecorderAbstractBaseClass):
    @property
    def record_filename(self): return ''
    @property
    def parsed_record_filename(self): return ''
    @property
    def last_record_filename(self): return ''
    def __init__(self):
        DoorPi().event_handler.register_action('OnSipPhoneDestroy', self.destroy)
        DoorPi().event_handler.register_event('OnRecorderStarted', __name__)
        DoorPi().event_handler.register_event('OnRecorderStopped', __name__)
        DoorPi().event_handler.register_event('OnRecorderCreated', __name__)
        DoorPi().event_handler('OnRecorderCreated', __name__)
    def start(self):
        return False
    def stop(self):
        return False
    def destroy(self):
        try: self.stop()
        except: pass
        DoorPi().event_handler.unregister_source(__name__, True)

class DummyPlayer(PlayerAbstractBaseClass):
    @property
    def player_filename(self): return ''
    def __init__(self):
        doorpi.DoorPi().event_handler.register_action('OnSipPhoneDestroy', self.destroy)
        doorpi.DoorPi().event_handler.register_event('OnPlayerStarted', __name__)
        doorpi.DoorPi().event_handler.register_event('OnPlayerStopped', __name__)
        doorpi.DoorPi().event_handler.register_event('OnPlayerCreated', __name__)
        doorpi.DoorPi().event_handler('OnPlayerCreated', __name__)

    def start(self): doorpi.DoorPi().event_handler('OnPlayerStarted', __name__)
    def stop(self):  doorpi.DoorPi().event_handler('OnPlayerStopped', __name__)
    def destroy(self):
        self.stop()
        doorpi.DoorPi().event_handler.unregister_source(__name__, True)
