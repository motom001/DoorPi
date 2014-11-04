#!/usr/bin/env python
# -*- coding: utf-8 -*-

#standard python libs
import logging # needed for logging
import logging.handlers # needed for log_rotation
import sys # need for except
import metadata

#third party libs
from daemon import runner

# own lib
import doorpi

LOG_FILENAME = '/var/log/doorpi/doorpi.log'

logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s]  \t[%(name)s] %(message)s')
log_rotating = logging.handlers.RotatingFileHandler(
    LOG_FILENAME, maxBytes=10000, backupCount=5
)
log_rotating.setFormatter(formatter)
logger.addHandler(log_rotating)

#console = logging.StreamHandler()
#console.setLevel(logging.DEBUG)
#console.setFormatter(formatter)
#logger.addHandler(console)

daemon_runner = runner.DaemonRunner(doorpi.DoorPi())
#This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve=[log_rotating.stream]

try:                        daemon_runner.do_action()
except Exception as ex:     logger.exception("Exception NameError: %s", ex)
finally:                    doorpi.DoorPi().destroy()
