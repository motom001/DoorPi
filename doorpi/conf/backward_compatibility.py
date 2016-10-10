#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

BACKWARD_COMPATIBILITY_KEYS = {
    'SIP-Phone': {
        'sipserver_server':             ('SIP-Phone', 'server'),
        'sipserver_username':           ('SIP-Phone', 'username'),
        'sipserver_password':           ('SIP-Phone', 'password'),
        'sipserver_realm':              ('SIP-Phone', 'realm'),
        'dialtone':                     ('DoorPi', 'dialtone'),
        'dialtone_renew_every_start':   ('DoorPi', 'dialtone_renew_every_start'),
        'dialtone_volume':              ('DoorPi', 'dialtone_volume'),
        'records':                      ('DoorPi', 'records'),
        'record_while_dialing':         ('DoorPi', 'record_while_dialing')
    }
}

def convert_config_to_json(config_object):
    return config_object