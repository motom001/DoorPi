import logging


logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)


def get(*args, **kwargs):
    try:
        if len(kwargs['name']) == 0: kwargs['name'] = ['']
        if len(kwargs['value']) == 0: kwargs['value'] = ['']
        return_dict = {}
        for section_request in kwargs['name']:
            for section in kwargs['DoorPiObject'].config.get_sections(section_request):
                return_dict[section] = {}
                for value_request in kwargs['value']:
                    for key in kwargs['DoorPiObject'].config.get_keys(section, value_request):
                        return_dict[section][key] = kwargs['DoorPiObject'].config \
                            .get_string(section, key)

        for section in list(return_dict.keys()):
            if len(return_dict[section]) == 0: del return_dict[section]

        return return_dict
    except Exception as exp:
        logger.exception(exp)
        return {'Error': f'could not create {__name__!s} object - {exp!s}'}


def is_active(doorpi_object):
    return True if doorpi_object.config else False
