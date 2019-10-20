import logging
from time import sleep

import doorpi
from . import Action


logger = logging.getLogger(__name__)


class HangupAction(Action):

    def __init__(self, waittime=0):
        self.__waittime = float(waittime)

    def __call__(self, event_id, extra):
        if self.__waittime:
            logger.info("[%s] Hanging up all calls in %s seconds", event_id, self.__waittime)
            sleep(self.__waittime)

        logger.info("[%s] Hanging up all calls", event_id)
        doorpi.DoorPi().sipphone.hangup()


instantiate = HangupAction
