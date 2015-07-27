#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

BACKWARD_COMPATIBILITY_KEYS = {
    'SIP-Phone': {
        # add 2015-07-27 by motom001
        'sipphone_server':      ('SIP-Phone', 'server'),
        'sipphone_username':    ('SIP-Phone', 'username'),
        'sipphone_password':    ('SIP-Phone', 'password'),
        'sipphone_realm':       ('SIP-Phone', 'realm')
    }
}
