#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

def get(*args, **kwargs):
    try:
        if len(kwargs['name']) == 0: kwargs['name'] = ['']
        if len(kwargs['value']) == 0: kwargs['value'] = ['']

        filter = kwargs['name'][0]
        try: max_count = int(kwargs['value'][0])
        except: max_count = 100

        return kwargs['DoorPiObject'].event_handler.db.get_event_log_entries(max_count, filter)
    except Exception as exp:
        logger.exception(exp)
        return {'Error': 'could not create '+str(__name__)+' object - '+str(exp)}

def is_active(doorpi_object):
    if len(doorpi_object.event_handler.db.get_event_log_entries(1, '')):
        return True
    else:
        return False
