#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

class KeyboardAbstractBaseClass(object):
    __InputPins = []
    __OutputPins = []
    __last_key = []

    def __init__(self): raise NotImplementedError("Subclasses should implement this!")
    def __del__(self): raise NotImplementedError("Subclasses should implement this!")
    def destroy(self): raise NotImplementedError("Subclasses should implement this!")

    def self_test(self): raise NotImplementedError("Subclasses should implement this!")
    #def get_last_key(self): raise NotImplementedError("Subclasses should implement this!")
    @property
    def last_key(self): return self.get_last_key()
    #def is_key_pressed(self): raise NotImplementedError("Subclasses should implement this!")
    @property
    def pressed_key(self): return self.is_key_pressed()
    #def which_keys_are_pressed(self): raise NotImplementedError("Subclasses should implement this!")
    @property
    def pressed_keys(self): return self.which_keys_are_pressed()
    def set_output(self, key, start_value = 1, end_value = 0,
                   timeout = 0.5, stop_pin = None, log_output = True
    ): raise NotImplementedError("Subclasses should implement this!")
