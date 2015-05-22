#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import importlib

def get(*args, **kwargs):
    try:
        if len(kwargs['name']) == 0: kwargs['name'] = ['']
        if len(kwargs['value']) == 0: kwargs['value'] = ['']

        status = {}
        for name_requested in kwargs['name']:
            if name_requested in 'sipphone':
                status['sipphone'] = get_install_status(['linphone', 'pjsua'])
            if name_requested in 'keyboard':
                status['keyboard'] = get_install_status(['pifacedigitalio', 'RPi.GPIO', 'watchdog', 'serial'])

        return status
    except Exception as exp:
        logger.exception(exp)
        return {'Error': 'could not create '+str(__name__)+' object - '+str(exp)}

def get_install_status(names):
    status = {}

    default_attr = ['__doc__', '__file__', '__name__', '__package__', '__path__', '__version__']

    for name in names:
        try:
            status[name] = {}
            package = importlib.import_module(name)
            content = dir(package)

            for attr in default_attr:
                if attr in content:
                    status[name][attr.replace('__', '')] = getattr(package, attr)
                else:
                    status[name][attr.replace('__', '')] = 'unknown'

            status[name]['installed'] = True
            #status[name]['content'] = content
        except Exception as exp:
            status[name] = {}
            status[name]['installed'] = False
            status[name]['error'] = str(exp)
    return status

def is_active(doorpi_object):
    return True
