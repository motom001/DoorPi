import logging


logger = logging.getLogger(__name__)


def get(*args, **kwargs):
    try:
        if len(kwargs['name']) == 0: kwargs['name'] = ['']
        if len(kwargs['value']) == 0: kwargs['value'] = ['']

        filter = kwargs['name'][0]
        try: max_count = int(kwargs['value'][0])
        except Exception: max_count = 100

        return kwargs['DoorPiObject'].event_handler.db.get_event_log(max_count, filter)
    except Exception as exp:
        logger.exception(exp)
        return {'Error': f'could not create {__name__!s} object - {exp!s}'}


def is_active(doorpi_object):
    if len(doorpi_object.event_handler.db.get_event_log_entries(1, '')):
        return True
    else:
        return False
