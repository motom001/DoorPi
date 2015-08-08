#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import doorpi

def control_config_get_value(section, key, default = '', store = 'True'):
    return doorpi.DoorPi().config.get_string(
        section = section,
        key = key,
        default = default,
        store_if_not_exists = True if store.lower() == 'true' else False
    )

def control_config_set_value(section, key, value, password = 'False'):
    return doorpi.DoorPi().config.set_value(
        section = section,
        key = key,
        value = value,
        password = True if password.lower() == 'true' else False
    )

def control_config_delete_key(section, key):
    return doorpi.DoorPi().config.delete_key(
        section = section,
        key = key
    )

def control_config_save(configfile = ""):
    return doorpi.DoorPi().config.save_config(
        configfile = configfile
    )

def control_config_get_configfile ():
    return doorpi.DoorPi().config.config_file or ''
