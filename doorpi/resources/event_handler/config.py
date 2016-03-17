# -*- coding: utf-8 -*-

from main import DOORPI
logger = DOORPI.register_modul(__name__)

class EventHandlerConfig:

    typ = {
        'type': 'string',
        'default': DOORPI.CONSTEVENTHANDLER_DB_TYP,
        'description': 'EventHandlerConfig_key_typ'
    }
    connection_string = DOORPI.EVENTHANDLER_DB_CONNECTIONSTRING
