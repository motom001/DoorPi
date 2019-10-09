import logging


logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)


def get(DoorPiObject, name=[], *args, **kwargs):
    logger.trace("Requested sipphone status with name=%s", name)
    if len(name) == 0:
        name = ["name", "current_call"]

    sipphone = DoorPiObject.sipphone
    status = {}

    if "name" in name:
        status["name"] = sipphone.get_name()

    if "current_call" in name:
        status["current_call"] = sipphone.dump_call()

    return status


def is_active(doorpi_object):
    return True if doorpi_object.sipphone else False
