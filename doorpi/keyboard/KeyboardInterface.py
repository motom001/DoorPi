#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import importlib

import doorpi
from keyboard.AbstractBaseClass import KeyboardAbstractBaseClass

class KeyboardImportError(ImportError): pass
class UnknownOutputPin(Exception): pass

def load_keyboard():
    config_keyboards = doorpi.DoorPi().config.get_keys(section = 'keyboards')
    if len(config_keyboards) > 0:
        logger.info("using multi-keyboard mode (keyboards: %s)", ', '.join(config_keyboards))
        return KeyboardHandler(config_keyboards)
    elif len(config_keyboards) is 1:
        logger.info("using single-keyboard mode by keyboards first and only key %s", config_keyboards[0])
        return load_single_keyboard(config_keyboards[0])
    else:
        logger.info("using single-keyboard mode")
        return load_single_keyboard()

def load_single_keyboard(keyboard_name = ''):
    conf_pre = ''
    conf_post = ''

    if keyboard_name is '':
        keyboard_type = doorpi.DoorPi().config.get('keyboard', 'typ', 'gpio').lower()
    else:
        conf_pre = keyboard_name+'_'
        keyboard_type = doorpi.DoorPi().config.get('keyboards', keyboard_name, 'gpio').lower()

    input_pins = doorpi.DoorPi().config.get_keys(conf_pre+'InputPins'+conf_post)
    output_pins = doorpi.DoorPi().config.get_keys(conf_pre+'OutputPins'+conf_post)
    bouncetime = doorpi.DoorPi().config.get_float(conf_pre+'keyboard'+conf_post, 'bouncetime', 2000)
    polarity = doorpi.DoorPi().config.get_int(conf_pre+'keyboard'+conf_post, 'polarity', 0)
    try:
        keyboard = importlib.import_module('keyboard.from_'+keyboard_type).get(
            input_pins = input_pins,
            output_pins = output_pins,
            bouncetime = bouncetime,
            polarity = polarity,
            keyboard_name = keyboard_name,
            keyboard_type = keyboard_type,
            conf_pre = conf_pre,
            conf_post = conf_post
        )
    except ImportError as exp:
        logger.exception('keyboard %s not found @ keyboard.from_%s (msg: %s)', keyboard_name, keyboard_type, exp)
        return None

    return keyboard

class KeyboardHandler(KeyboardAbstractBaseClass):
    @property
    def name(self):
        keyboard_names = []
        for Keyboard in self.__keyboards:
            keyboard_names.append(Keyboard)
        return 'KeyboardHandler (with %s)' % ', '.join(keyboard_names)

    @property
    def input_pins(self):
        return_list = []
        for Keyboard in self.__keyboards:
            for input_pin in self.__keyboards[Keyboard].input_pins:
                return_list.append(Keyboard+'.'+str(input_pin))
        return return_list

    @property
    def output_pins(self):
        return_list = []
        for Keyboard in self.__keyboards:
            for pin in self.__keyboards[Keyboard].output_pins:
                return_list.append(Keyboard+'.'+str(pin))
        return return_list

    @property
    def output_status(self):
        return_dict = {}
        for Keyboard in self.__keyboards:
            for pin in self.__keyboards[Keyboard].output_pins:
                return_dict[Keyboard+'.'+str(pin)] = self.__keyboards[Keyboard].status_output(pin)
        return return_dict

    @property
    def loaded_keyboards(self):
        return_dict = {}
        for keyboard in self.__keyboards:
            return_dict[keyboard] = self.__keyboards[keyboard].keyboard_typ
        return return_dict

    def __init__(self, config_keyboards):
        self.__OutputMappingTable = {}
        self.__keyboards = {}
        for keyboard_name in config_keyboards:
            logger.info("try to add keyboard '%s' to handler", keyboard_name)
            self.__keyboards[keyboard_name] = load_single_keyboard(keyboard_name)
            if self.__keyboards[keyboard_name] is None:
                logger.error("couldn't load keyboard %s", keyboard_name)
                del self.__keyboards[keyboard_name]

            output_pins = doorpi.DoorPi().config.get_keys(keyboard_name+'_OutputPins')
            for output_pin in output_pins:
                output_pin_name = doorpi.DoorPi().config.get(keyboard_name+'_OutputPins', output_pin)
                if output_pin_name in self.__OutputMappingTable:
                    logger.warning('overwrite existing name of outputpin "%s" (exists in %s and %s)',
                        output_pin_name,
                        self.__OutputMappingTable[output_pin_name],
                        keyboard_name
                    )
                self.__OutputMappingTable[output_pin_name] = keyboard_name

        if len(self.__keyboards) is 0: raise KeyboardImportError('no keyboards found')


    def destroy(self):
        try:
            for Keyboard in self.__keyboards:
                self.__keyboards[Keyboard].destroy()
        except: pass

    def set_output(self, pin, value, log_output = True):
        if pin not in self.__OutputMappingTable:
            raise UnknownOutputPin('outputpin with name %s is unknown %s' % (pin, self.__OutputMappingTable))
        self.__keyboards[self.__OutputMappingTable[pin]].set_output(pin, value, log_output)

    def status_input(self, pin):
        for keyboard in self.__keyboards:
            if pin.startswith(keyboard+'.'):
                return self.__keyboards[keyboard].status_input(pin[len(keyboard+'.'):])
        return None

    def status_output(self, pin):
        for keyboard in self.__keyboards:
            if pin.startswith(keyboard+'.'):
                return self.__keyboards[keyboard].status_output(pin[len(keyboard+'.'):])
        return None

    __del__ = destroy