# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import importlib
import doorpi

class SipphoneModuleException(Exception): pass

def load_sipphone():
    conf_pre = ''
    conf_post = ''

    sipphone_name = doorpi.DoorPi().config.get("SIP-Phone", "sipphonetyp", "dummy")

    try:
        sipphone = importlib \
                .import_module("doorpi.sipphone.from_"+sipphone_name) \
                .get(sipphone_name = sipphone_name, conf_pre = conf_pre, conf_post = conf_post)
    except Exception as ex:
        raise SipphoneModuleException("Error loading SIP phone module \"{}\"".format(sipphone_name), ex)

    return sipphone
