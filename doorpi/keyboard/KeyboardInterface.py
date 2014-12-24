#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import doorpi

def detect_keyboard():
    keyboards = dict(
        autodetect = autodetect,
        piface = load_piface,
        gpio = load_gpio
    )

    config_value = doorpi.DoorPi().config.get(
        section = 'DoorPi',
        key = 'keyboard',
        default = 'autodetect'
    )
    if config_value not in keyboards.keys():
        raise Exception(
            'Keyboard {0} in configfile is unknown. - possible values are {1}'.format(
            config_value, keyboards.keys())
        )

    return keyboards[config_value](
        input_pins = doorpi.DoorPi().config.get_keys('InputPins'),
        output_pins = doorpi.DoorPi().config.get_keys('OutputPins')
    )

#TODO: Don't repeat yourself -> only one function to load module
def autodetect(input_pins, output_pins):
    logger.trace('autodetect')
    try: return load_piface(input_pins, output_pins)
    except ImportError: logger.info('could not load keyboard piface')

    try: return load_gpio(input_pins, output_pins)
    except ImportError: logger.info('could not load keyboard gpio')

    raise Exception('keyboard autodetect failed')

def load_piface(input_pins, output_pins):
    logger.trace('load_piface')
    import keyboard.from_piface
    return keyboard.from_piface.PiFace(
        input_pins = input_pins,
        output_pins = output_pins
    )

def load_gpio(input_pins, output_pins):
    logger.trace('load_gpio')
    import keyboard.from_gpio
    return keyboard.from_gpio.GPIO(
        input_pins = input_pins,
        output_pins = output_pins
    )
