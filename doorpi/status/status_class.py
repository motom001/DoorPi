#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import json
from datetime import datetime

import importlib

MODULES = [
    'status_time',
    #'additional_informations',
    'config',
    'keyboard',
    'sipphone',
    'event_handler',
    'history_event',
    'history_snapshot',
    #'history_action',
    'environment',
    'webserver'
]

def collect_status(doorpi_object, modules = MODULES, value = list(), name = list()):
    return DoorPiStatus(doorpi_object, modules, value, name)

class DoorPiStatus(object):

    @property
    def dictionary(self): return self.__status

    @property
    def json(self): return json.dumps(self.__status)

    @property
    def json_beautified(self): return json.dumps(self.__status, sort_keys=True, indent=4)

    def __init__(self, DoorPiObject, modules = MODULES, value = list(), name = list()):
        self.__status = {}
        self.collect_status(DoorPiObject, modules, value, name)

    def collect_status(self, DoorPiObject, modules = MODULES, value = list(), name = list()):
        if len(modules) == 0: modules = MODULES

        for module in modules:
            if module not in MODULES:
                logger.warning('skipping unknown status module %s', module)
                continue
            self.__status[module] = {}
            try:
                self.__status[module] = importlib.import_module('doorpi.status.status_lib.'+module).get(
                    modules = modules,
                    module = module,
                    name = name,
                    value = value,
                    DoorPiObject = DoorPiObject
                )
            except ImportError as exp:
                logger.exception('status %s not found @ status.status_lib.%s (msg: %s)', module, module, exp)
            except Exception as exp:
                logger.exception('status %s error (msg: %s)', module, exp)
