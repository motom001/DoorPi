#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

BACKWARD_COMPATIBILITY_KEYS = {
    'SIP-Phone': {
        'sipphone_server':      ('SIP-Phone', 'server'),
        'sipphone_username':    ('SIP-Phone', 'username'),
        'sipphone_password':    ('SIP-Phone', 'password'),
        'sipphone_realm':       ('SIP-Phone', 'realm')
    },
    'DoorPi': {
        'dialtone':                     ('SIP-Phone', 'dialtone'),
        'dialtone_renew_every_start':   ('SIP-Phone', 'dialtone_renew_every_start'),
        'dialtone_volume':              ('SIP-Phone', 'dialtone_volume'),
        'records':                      ('SIP-Phone', 'records'),
        'record_while_dialing':         ('SIP-Phone', 'record_while_dialing')
    }
}
