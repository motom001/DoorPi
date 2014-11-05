#!/usr/bin/env python
# -*- coding: utf-8 -*-

#standard python libs
import logging # needed for logging
import logging.handlers # needed for log_rotation
import sys # need for except
import metadata

# own lib
import doorpiweb

LOG_FILENAME = '/var/log/doorpiweb/doorpiweb.log'

logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s [%(levelname)s]  \t[%(name)s] %(message)s')

#log_rotating = logging.handlers.RotatingFileHandler(
#    LOG_FILENAME, maxBytes=10000, backupCount=5
#)
#log_rotating.setFormatter(formatter)
#logger.addHandler(log_rotating)

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)
logger.addHandler(console)

try:                        doorpiweb.DoorPiWeb().run()
except KeyboardInterrupt:   logger.info("KeyboardInterrupt -> DoorPiWeb will shutdown")
except Exception as ex:     logger.exception("Exception NameError: %s", ex)
finally:                    doorpiweb.DoorPiWeb().destroy()
