#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

SIPPHONE_SECTION = 'SIP-Phone'
DOORPI_SECTION = 'DoorPi'

from doorpi.action.base import SingleAction
import doorpi
import subprocess as sub

conf = doorpi.DoorPi().config

def take_snapshot(size, path, max):
    if not os.path.exists(path):
        logger.info('Path (%s) does not exist - creating it now', path)
        os.makedirs(path)

    lastFile = getLastFilename(path)
    lastNr = 1
    if (len(lastFile) > 0):
        lastNr = int(lastFile[:lastFile.rfind(".jpg")])
        if (lastNr+1 <= max):
            lastNr = lastNr + 1
    else:
        lastNr = 1
    imageFilename = path + str(lastNr) + ".jpg"
    # fswebcam automatically selects the first video device
    command = "fswebcam --top-banner -b --font luxisr:20 -r " + size + " " + imageFilename
    p = sub.Popen(command, shell=True, stdout=sub.PIPE, stderr=sub.PIPE)
    output, errors = p.communicate()
    if (len(errors) > 0):
        logger.error('error creating snapshot - maybe fswebcam is missing')
    else:
        logger.info('snapshot created: %s', imageFilename)
    return


def getLastFilename(path):
    files = [s for s in os.listdir(path)
         if os.path.isfile(os.path.join(path, s))]
    files.sort(key=lambda s: os.path.getmtime(os.path.join(path, s)))
    if (len(files) == 0):
        return ''
    return files[len(files)-1]

def get(parameters):
    conf = doorpi.DoorPi().config
    snapshot_size = conf.get_string(DOORPI_SECTION, 'snapshot_size', '1280x720')
    snapshot_path = conf.get_string_parsed(DOORPI_SECTION, 'snapshot_path', '!BASEPATH!/../DoorPiWeb/snapshots/')
    number_of_snapshots = conf.get_int(DOORPI_SECTION, 'number_of_snapshots', 10)

    if len(conf.get(SIPPHONE_SECTION, 'capture_device', '')) > 0:
        return SnapShotAction(take_snapshot, size = snapshot_size, path = snapshot_path, max = number_of_snapshots)
    logger.warning('can not create snapshot - video disabled')

class SnapShotAction(SingleAction):
    pass
