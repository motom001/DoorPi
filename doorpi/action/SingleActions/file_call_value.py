#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import doorpi
from doorpi.action.base import SingleAction

def call_phonenumber_from_file(filename):
    try:
        with open(doorpi.DoorPi().parse_string(filename), 'r') as f:
            phonenumber = f.readline().strip(' \t\n\r')

        logger.debug("firing sipphone.call for this number: %s", phonenumber)
        doorpi.DoorPi().sipphone.call(phonenumber)
        logger.debug("finished sipphone.call for this number: %s", phonenumber)

    except Exception as ex:
        logger.exception("couldn't get phonenumber from file (%s)", ex)
        return False
    return True

def get(parameters):
    return CallPhoneNumberFromFileAction(call_phonenumber_from_file, filename = parameters)

class CallPhoneNumberFromFileAction(SingleAction):
    pass
