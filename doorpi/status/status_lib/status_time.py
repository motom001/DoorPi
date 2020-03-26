from datetime import datetime


def get(doorpi_obj, name, value):
    del doorpi_obj, name, value
    return str(datetime.now())


def is_active(doorpi_object):
    del doorpi_object
    return True
