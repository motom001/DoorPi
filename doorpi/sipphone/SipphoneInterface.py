#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import doorpi

def get_sipphones():
    return dict(
        autodetect = autodetect,
        pjsua = load_pjsua,
        pjsip = load_pjsua
    )

def load_sipphone():
    sipphones = get_sipphones()
    config_value = doorpi.DoorPi().config.get('SIP-Phone', 'sipphonetyp', 'autodetect')

    if config_value not in sipphones.keys():
        raise Exception(
            'Sipphone {0} in configfile is unknown. - possible values are {1}'.format(
            config_value, keyboards.keys())
        )
    return sipphones[config_value]()

def load_pjsua():
    logger.trace('load_pjsua')
    import from_pjsua
    return from_pjsua.Pjsua()

def autodetect():
    sipphones = get_sipphones()
    for sipphone in sipphones.keys():
        if sipphone is not "autodetect":
            logger.trace('try to load %s', sipphone)
            try: return sipphones[sipphone]()
            except ImportError: logger.info('could not load sipphone %s', sipphone)
            except Exception as ex: logger.exception('undefined error while loading sipphone %s (%s)', sipphone, ex)

    raise Exception('no valid sipphone found')