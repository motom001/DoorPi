#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from datetime import datetime

def get(*args, **kwargs):
    return str(datetime.now())

def is_active(doorpi_object):
    return True
