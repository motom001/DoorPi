#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from datetime import datetime

def get(*args, **kwargs):
    try:
        if len(kwargs['name']) == 0: kwargs['name'] = ['']
        if len(kwargs['value']) == 0: kwargs['value'] = ['']

        keyboard = kwargs['DoorPiObject'].keyboard

        status = {}

        for name_requested in kwargs['name']:
            if name_requested in 'name':
                status['name'] = keyboard.name

            if name_requested in 'input':
                status['input'] = {}
                for value_requested in kwargs['value']:
                    for input_pin in keyboard.input_pins:
                        if value_requested in input_pin:
                            status['input'][input_pin] = keyboard.status_input(input_pin)

            if name_requested in 'output':
                status['output'] = keyboard.output_status
                for value_requested in kwargs['value']:
                    for output_pin in status['output'].keys():
                        if value_requested not in output_pin:
                            del status['output'][output_pin]
        return status

    except Exception as exp:
        logger.exception(exp)
        return {'Error': 'could not create keyboard object - '+str(exp)}

def is_active(doorpi_object):
    try:
        return True if doorpi_object.keyboard.name else False
    except:
        return False
