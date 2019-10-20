import logging

import doorpi
from . import Action

logger = logging.getLogger(__name__)


class CallFromFileAction(Action):

    def __init__(self, filename):
        self.__filename = filename

    def __call__(self, event_id, extra):
        try:
            with open(doorpi.DoorPi().parse_string(self.__filename), "r") as f:
                url = f.readline()

            if not url:
                raise ValueError(f"File {self.__filename} is empty")

            doorpi.DoorPi().sipphone.call(url)
        except OSError as err:
            raise RuntimeError(f"Cannot read target URL from file {self.__filename}") from err


instantiate = CallFromFileAction
