import logging
import subprocess

import doorpi
from . import Action


logger = logging.getLogger(__name__)


class OSExecuteAction(Action):

    def __init__(self, *cmd):
        self.__cmd = ",".join(cmd)

    def __call__(self, event_id, extra):
        logger.info("[%s] Executing shell command: %s", event_id, self.__cmd)
        result = subprocess.run(self.__cmd, shell=True)

        if result.returncode == 0:
            logger.info("[%s] Command returned successfully", event_id)
        else:
            logger.info("[%s] Command returned with code %d", event_id, result.returncode)


instantiate = OSExecuteAction
