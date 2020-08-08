"""Actions related to executing other processes: os_execute"""

import logging
import subprocess

from . import action

LOGGER = logging.getLogger(__name__)


@action("exec")
@action("os_execute")
class OSExecuteAction:
    """Executes a command"""

    def __init__(self, *cmd):
        self.__cmd = ",".join(cmd)

    def __call__(self, event_id, extra):
        LOGGER.info("[%s] Executing shell command: %s", event_id, self.__cmd)
        result = subprocess.run(self.__cmd, shell=True, check=False)

        if result.returncode == 0:
            LOGGER.info("[%s] Command returned successfully", event_id)
        else:
            LOGGER.info(
                "[%s] Command returned with code %d",
                event_id, result.returncode)

    def __str__(self):
        return f"Run shell code {self.__cmd}"

    def __repr__(self):
        return f"os_execute:{self.__cmd}"
