import doorpi


def control_config_get_value(section, key, default="", store="True"):
    del store
    try:
        return doorpi.INSTANCE.config[".".join((section, key))]
    except KeyError:
        return default


def control_config_set_value(section, key, value, password=False):
    del password
    try:
        doorpi.INSTANCE.config[".".join((section, key))] = value
    except (KeyError, TypeError, ValueError):
        return False
    else:
        return True


def control_config_delete_key(section, key):
    return False  # FIXME NYI


def control_config_save(configfile=""):
    return doorpi.INSTANCE.config.save(configfile)
