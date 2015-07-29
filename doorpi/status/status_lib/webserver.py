#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

def get(*args, **kwargs):
    try:
        if len(kwargs['name']) == 0: kwargs['name'] = ['']
        if len(kwargs['value']) == 0: kwargs['value'] = ['']

        webserver = kwargs['DoorPiObject'].webserver

        status = {}
        for name_requested in kwargs['name']:
            if name_requested in 'config_status':
                status[name_requested] = webserver.config_status

            if name_requested in 'sessions':
                status[name_requested] = webserver.config_status

        return status
    except Exception as exp:
        logger.exception(exp)
        return {'Error': 'could not create '+str(__name__)+' object - '+str(exp)}

def is_active(doorpi_object):
    return True if doorpi_object.webserver else False
