import logging

import doorpi
from . import Action


logger = logging.getLogger(__name__)


class LogAction(Action):

    def __init__(self, *msg):
        self.__msg = ",".join(msg)

    def __call__(self, event_id, extra):
        logger.info("[%s] %s", event_id, doorpi.DoorPi().parse_string(self.__msg))

    def __str__(self):
        return f"Log the message {self.__msg}"

    def __repr__(self):
        return f"{__name__.split('.')[-1]}:{self.__msg}"


instantiate = LogAction
