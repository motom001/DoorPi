# -*- coding: utf-8 -*-
import doorpi
from doorpi.action.base import SingleAction
from doorpi.status.status_class import DoorPiStatus

from io import open

import logging
logger = logging.getLogger(__name__)
logger.debug('%s loaded', __name__)


def write_statusfile(filename, content):
    try:
        filename = doorpi.DoorPi().parse_string(filename)
        content = doorpi.DoorPi().parse_string(content.strip() + '\n')

        try:
            doorpi_status = DoorPiStatus(doorpi.DoorPi())
            doorpi_status_json_beautified = doorpi_status.json_beautified
            doorpi_status_json = doorpi_status.json

            content = content.replace(
                '!DOORPI_STATUS.json_beautified!', doorpi_status_json_beautified)
            content = content.replace(
                '!DOORPI_STATUS.json!', doorpi_status_json)
        except:
            logger.exception('error while creating status')
    except:
        logger.warning(
            'while action statusfile - error to get DoorPi().parse_string')
        return False

    try:
        with open(filename, 'w') as file
        file.write(filecontent)
    except IOError as e:
        logger.warning(
            ('while action statusfile - I/O error({0}): {1}').format(e.errno, e.strerror))
        return False
    return True


def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) < 2:
        return None

    filename = parameter_list[0]
    content = ''.join(parameter_list[1:])
    return StatusFileAction(write_statusfile, filename, content)


class StatusFileAction(SingleAction):
    pass
