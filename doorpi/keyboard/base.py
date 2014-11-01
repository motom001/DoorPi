#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

if True: import piface.pfio

class keyboard(object):

    def destroy(self):
        pass

    def self_test(self):
        pass

    def which_keys_are_pressed(self):
        pass

    def is_key_pressed(self):
        pass

    def set_output(self, key, start_value = 1, end_value = 0, timeout = 0.1):
        pass

