#!/usr/bin/env python
# -*- coding: utf-8 -*-

#standard python libs
import logging # needed for logging
import logging.handlers # needed for log_rotation
import sys # need for except
import metadata

# own lib
import doorpi

TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")
def trace(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    self._log(TRACE_LEVEL, message, args, **kws)
logging.Logger.trace = trace

LOG_FILENAME = '/var/log/doorpi/doorpi.log'

logger = logging.getLogger('')
logger.setLevel(TRACE_LEVEL)
formatter = logging.Formatter('%(asctime)s [%(levelname)s]  \t[%(name)s] %(message)s')

#log_rotating = logging.handlers.RotatingFileHandler(
#    LOG_FILENAME, maxBytes=10000, backupCount=5
#)
#log_rotating.setFormatter(formatter)
#log_rotating.setLevel(logging.DEBUG)
#logger.addHandler(log_rotating)

console = logging.StreamHandler()
console.setLevel(TRACE_LEVEL)
console.setFormatter(formatter)
logger.addHandler(console)

try:                        doorpi.DoorPi().run()
except KeyboardInterrupt:   logger.info("KeyboardInterrupt -> DoorPi will shutdown")
except Exception as ex:     logger.exception("Exception NameError: %s", ex)
finally:                    doorpi.DoorPi().destroy()
