#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

DOORPI_SECTION = 'DoorPi'

def get(*args, **kwargs):
    files = dict()
    try:
        if len(kwargs['name']) == 0: kwargs['name'] = ['']
        if len(kwargs['value']) == 0: kwargs['value'] = ['']

        path = kwargs['DoorPiObject'].config.get_string_parsed(DOORPI_SECTION, 'snapshot_path')
        if os.path.exists(path):
            files = [os.path.join(path,i) for i in os.listdir(path)]
            files = sorted(files, key=os.path.getmtime)
            # because path is added by webserver automatically
            if path.find('DoorPiWeb'):
                    changedpath = path[path.find('DoorPiWeb')+len('DoorPiWeb'):]
                    files = [f.replace(path, changedpath) for f in files]
        return files
    except Exception as exp:
        logger.exception(exp)
        return {'Error': 'could not create '+str(__name__)+' object - '+str(exp)}
