import logging

import doorpi
from . import Action


logger = logging.getLogger(__name__)


class CallAction(Action):
    def __init__(self, url):
        self.__url = url

    def __call__(self, event_id, extra):
        doorpi.DoorPi().sipphone.call(self.__url)

    def __str__(self):
        return f"Call {self.__url}"

    def __repr__(self):
        return f"{__name__.split('.')[-1]}:{self.__url}"


instantiate = CallAction
