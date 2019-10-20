import logging

import doorpi
from . import Action


logger = logging.getLogger(__name__)


class LogAction(Action):

    def __init__(self, *msg):
        self.__msg = ",".join(msg)

    def __call__(self, event_id, extra):
        logger.info("[%s] %s", event_id, doorpi.DoorPi().parse_string(self.__msg))


instantiate = LogAction
