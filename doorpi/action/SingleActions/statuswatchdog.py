from doorpi.action.base import SingleAction
from io import open

import logging
logger = logging.getLogger(__name__)
logger.debug('%s loaded', __name__)


def write_status_watchdog(watchdog_path, timeout):
    timeout = int(timeout)

    try:
        with open(watchdog_path, 'w+') as watchdog:
            watchdog.write('\n')
            watchdog.flush()
    except Exception as exp:
        logger.warning('error opening watchdog file %s' % exp)
        return False
    return True


def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) != 1 and len(parameter_list) != 2:
        return None

    watchdog = parameter_list[0]
    timeout = (5 if len(parameter_list) != 2 else int(parameter_list[1]))
    return StatusWatchdogAction(write_status_watchdog, watchdog, timeout)


class StatusWatchdogAction(SingleAction):
    pass
