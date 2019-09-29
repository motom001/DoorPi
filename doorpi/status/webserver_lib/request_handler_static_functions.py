import logging
import doorpi


logger = logging.getLogger(__name__)


def control_config_get_value(section, key, default='', store='True'):
    return doorpi.DoorPi().config.get_string(
        section=section,
        key=key,
        default=default,
    )


def control_config_set_value(section, key, value, password='False'):
    return doorpi.DoorPi().config.set_value(
        section=section,
        key=key,
        value=value,
    )


def control_config_delete_key(section, key):
    return doorpi.DoorPi().config.delete_key(
        section=section,
        key=key
    )


def control_config_save(configfile=""):
    return doorpi.DoorPi().config.save_config(
        configfile=configfile
    )


def control_config_get_configfile():
    return doorpi.DoorPi().config.config_file or ''
