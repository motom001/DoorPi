#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

class ActionHandler():

    __active_actions = []

    def __init__(self):
        logger.debug("__init__")

    def __del__(self):
        logger.debug("__del__")

    def check(self):
        for action in self.__active_actions:

            return action