#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import importlib

import doorpi
from doorpi.keyboard.AbstractBaseClass import KeyboardAbstractBaseClass

class KeyboardImportError(ImportError): pass
class UnknownOutputPin(Exception): pass

def load_keyboard():
    config_keyboards = doorpi.DoorPi().config.get_keys(section = 'keyboards')
    if len(config_keyboards) > 0:
        logger.info("using multi-keyboard mode (keyboards: %s)", ', '.join(config_keyboards))
        return KeyboardHandler(config_keyboards)
    else:
        logger.info("using multi-keyboard mode with dummy keyboard")
        return KeyboardHandler(['dummy'])

def load_single_keyboard(keyboard_name):
    conf_pre = keyboard_name+'_'
    conf_post = ''

    keyboard_type = doorpi.DoorPi().config.get('keyboards', keyboard_name, 'dummy').lower()
    store_if_not_exists = False if keyboard_type == "dummy" else True

    section_name = conf_pre+'keyboard'+conf_post
    input_pins = doorpi.DoorPi().config.get_keys(conf_pre+'InputPins'+conf_post)
    output_pins = doorpi.DoorPi().config.get_keys(conf_pre+'OutputPins'+conf_post)
    bouncetime = doorpi.DoorPi().config.get_float(section_name, 'bouncetime', 2000,
                                                  store_if_not_exists=store_if_not_exists)
    polarity = doorpi.DoorPi().config.get_int(section_name, 'polarity', 0,
                                              store_if_not_exists=store_if_not_exists)
    pressed_on_key_down = doorpi.DoorPi().config.get_bool(section_name, 'pressed_on_keydown',
                                                          True, store_if_not_exists=store_if_not_exists)
    try:
        keyboard = importlib.import_module('doorpi.keyboard.from_'+keyboard_type).get(
            input_pins=input_pins,
            output_pins=output_pins,
            bouncetime=bouncetime,
            polarity=polarity,
            keyboard_name=keyboard_name,
            keyboard_type=keyboard_type,
            conf_pre=conf_pre,
            conf_post=conf_post,
            pressed_on_key_down=pressed_on_key_down
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
            logger.info("trying to add keyboard '%s' to handler", keyboard_name)
            self.__keyboards[keyboard_name] = load_single_keyboard(keyboard_name)
            if self.__keyboards[keyboard_name] is None:
                logger.error("couldn't load keyboard %s", keyboard_name)
                del self.__keyboards[keyboard_name]
                continue

            output_pins = doorpi.DoorPi().config.get_keys(keyboard_name+'_OutputPins')
            for output_pin in output_pins:
                output_pin_name = doorpi.DoorPi().config.get(keyboard_name+'_OutputPins', output_pin)
                if output_pin_name in self.__OutputMappingTable:
                    logger.warning('overwriting existing name of outputpin "%s" (exists in %s and %s)',
                        output_pin_name,
                        self.__OutputMappingTable[output_pin_name],
                        keyboard_name
                    )
                self.__OutputMappingTable[output_pin_name] = keyboard_name

        if len(self.__keyboards) is 0:
            logger.error('No Keyboards loaded - load dummy!')
            self.__keyboards['dummy'] = load_single_keyboard('dummy')

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