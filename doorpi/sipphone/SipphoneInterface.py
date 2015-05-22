#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import importlib
import doorpi

class SipphoneNotExists(Exception): pass

def load_sipphone():
    conf_pre = ''
    conf_post = ''

    sipphone_name = doorpi.DoorPi().config.get('SIP-Phone', 'sipphonetyp', 'dummy')
    try:
        sipphone = importlib.import_module('sipphone.from_'+sipphone_name).get(
            sipphone_name = sipphone_name,
            conf_pre = conf_pre,
            conf_post = conf_post
        )
    except ImportError as exp:
        logger.exception('sipphone %s not found @ sipphone.from_%s', sipphone_name, sipphone_name)
        raise SipphoneNotExists('sipphone %s not found (%s)'%(sipphone_name, str(exp)))

    return sipphone
