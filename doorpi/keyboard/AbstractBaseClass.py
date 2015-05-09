#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import doorpi

HIGH_LEVEL = ['1', 'high', 'on', 'true']
LOW_LEVEL = ['0', 'low', 'off', 'false']

class KeyboardAbstractBaseClass(object):

    ############## methods to implement ##############
    def __init__(self): raise NotImplementedError("Subclasses should implement this!")
    #def destroy(self): pass #logger.warning("Subclasses should implement this!")
    def self_test(self): pass # optional - raise NotImplementedError("Subclasses should implement this!")
    def status_input(self, pin): raise NotImplementedError("Subclasses should implement this!")
    def set_output(self, pin, value, log_output = True): raise NotImplementedError("Subclasses should implement this!")
    ############ ############ ############ ############

    keyboard_name = ''
    @property
    def keyboard_typ(self): return self.__class__.__name__
    @property
    def name(self):
        if self.keyboard_name is '': return '%s Keyboard' % self.keyboard_typ
        else: return '%s (Typ: %s) Keyboard' % (self.keyboard_name, self.keyboard_typ)

    _InputPins = []
    @property
    def input_pins(self): return self._InputPins
    _OutputPins = []
    @property
    def output_pins(self): return self._OutputPins
    _OutputStatus = {}
    @property
    def output_status(self): return self._OutputStatus
    last_key = None
    #@property
    #def last_key(self): return self._last_key
    @property
    def additional_info(self): return {
        'keyboard_name'       : self.keyboard_name,
        'keyboard_typ'        : self.keyboard_typ,
        'name'                : self.name,
        'pin'                 : self.last_key
    }
    @property
    def pressed_keys(self):
        pressed_keys = []
        for input_pin in self._InputPins:
            if self.status_inputpin(input_pin):
                pressed_keys.append(input_pin)
        return pressed_keys
    @property
    def pressed_key(self):
        pressed_keys = self.pressed_keys()
        if len(pressed_keys) > 0: return pressed_keys[0]
        else: return None

    def status_output(self, pin):
        return self._OutputStatus[pin]

    def _register_EVENTS_for_pin(self, pin, name):
        for event in ['OnKeyPressed', 'OnKeyUp', 'OnKeyDown']:
            doorpi.DoorPi().event_handler.register_event(event, name)
            doorpi.DoorPi().event_handler.register_event(event+'_'+str(pin), name)
            doorpi.DoorPi().event_handler.register_event(event+'_'+self.keyboard_name+'.'+str(pin), name)

    def _fire_EVENT(self, event_name, pin, name):
        if self.keyboard_name == '':
            doorpi.DoorPi().keyboard.last_key = self.last_key = pin
        else:
            doorpi.DoorPi().keyboard.last_key = self.last_key = self.keyboard_name+'.'+str(pin)
        doorpi.DoorPi().event_handler(event_name, name, self.additional_info)
        doorpi.DoorPi().event_handler(event_name+'_'+str(pin), name, self.additional_info)
        doorpi.DoorPi().event_handler(event_name+'_'+self.keyboard_name+'.'+str(pin), name, self.additional_info)

    def _fire_OnKeyUp(self, pin, name): self._fire_EVENT('OnKeyUp', pin, name)
    def _fire_OnKeyDown(self, pin, name): self._fire_EVENT('OnKeyDown', pin, name)
    def _fire_OnKeyPressed(self, pin, name): self._fire_EVENT('OnKeyPressed', pin, name)

    get_input = status_input
    status_inputpin = status_input
    get_output = status_output
    get_last_key = last_key
    which_keys_are_pressed = pressed_keys
    #__del__ = destroy
