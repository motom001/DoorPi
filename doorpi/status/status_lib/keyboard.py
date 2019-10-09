import logging
from datetime import datetime


logger = logging.getLogger(__name__)


def get(name=[], value=[], DoorPiObject=[], **kwargs):
    kb = DoorPiObject.keyboard
    status = {}

    for name_requested in name:
        if name_requested == 'name':
            status['name'] = "Keyboard handler"
        elif name_requested == 'input':
            status['input'] = {}
            for pin in value:
                status["input"][pin] = keyboard.input(pin)
        else: status[name_requested] = {"Error": "unsupported operation"}
    return status


def is_active(doorpi_object):
    try:
        return True if doorpi_object.keyboard.name else False
    except Exception: return False
