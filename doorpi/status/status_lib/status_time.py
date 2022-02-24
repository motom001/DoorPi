
from datetime import datetime
import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)


def get(*args, **kwargs):
    return str(datetime.now())


def is_active(doorpi_object):
    return True
