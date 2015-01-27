#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

class SipphoneAbstractBaseClass(object):

    def __init__(self): raise NotImplementedError("Subclasses should implement this!")
    def config(self, **kwargs): raise NotImplementedError("Subclasses should implement this!")
    def start(self): raise NotImplementedError("Subclasses should implement this!")
    def stop(self): raise NotImplementedError("Subclasses should implement this!")
    def destroy(self): raise NotImplementedError("Subclasses should implement this!")
    def call(self, number): raise NotImplementedError("Subclasses should implement this!")
    def is_admin_number(self, number): raise NotImplementedError("Subclasses should implement this!")
    def __del__(self): self.destroy()

class RecorderAbstractBaseClass(object):

    def __init__(self): raise NotImplementedError("Subclasses should implement this!")
    def config(self, **kwargs): raise NotImplementedError("Subclasses should implement this!")
    def start(self): raise NotImplementedError("Subclasses should implement this!")
    def stop(self): raise NotImplementedError("Subclasses should implement this!")
    def destroy(self): raise NotImplementedError("Subclasses should implement this!")
    def __del__(self): self.destroy()

class PlayerAbstractBaseClass(object):

    def __init__(self): raise NotImplementedError("Subclasses should implement this!")
    def config(self, **kwargs): raise NotImplementedError("Subclasses should implement this!")
    def start(self): raise NotImplementedError("Subclasses should implement this!")
    def stop(self): raise NotImplementedError("Subclasses should implement this!")
    def destroy(self): raise NotImplementedError("Subclasses should implement this!")
    def __del__(self): self.destroy()