"""Actions related to logging: log"""

import logging

import doorpi
from . import action


LOGGER = logging.getLogger(__name__)


@action("log")
class LogAction:
    """Outputs a custom message to the log."""

    def __init__(self, *msg):
        self.__msg = ",".join(msg)

    def __call__(self, event_id, extra):
        LOGGER.info("[%s] %s", event_id, doorpi.DoorPi().parse_string(self.__msg))

    def __str__(self):
        return f"Log the message {self.__msg}"

    def __repr__(self):
        return f"log:{self.__msg}"
