import logging

from datetime import datetime


logger = logging.getLogger(__name__)


def get(*args, **kwargs):
    return str(datetime.now())


def is_active(doorpi_object):
    return True
