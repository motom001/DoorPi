#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import time

class SingleActionBaseClass():

    __starttime = None
    __max_duration = 0

    def __init__(self):
        logger.debug("__init__")
        self.__starttime = time.time()

    def __del__(self):
        logger.debug("__del__")

    def is_valid(self):
        if self.__starttime is None: return False
        if self.__max_duration is 0: return False
        if self.__max_duration is -1: return True
        if self.__starttime + self.__max_duration <= time.time(): return False
        return False

    def fire(self):
        pass