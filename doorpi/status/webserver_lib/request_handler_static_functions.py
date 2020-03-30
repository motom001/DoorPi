import doorpi


def control_config_get_value(section, key, default="", store="True"):
    del store
    return doorpi.INSTANCE.config.get_string(
        section=section,
        key=key,
        default=default,
    )


def control_config_set_value(section, key, value, password=False):
    del password
    return doorpi.INSTANCE.config.set_value(
        section=section,
        key=key,
        value=value,
    )


def control_config_delete_key(section, key):
    return doorpi.INSTANCE.config.delete_key(
        section=section,
        key=key
    )


def control_config_save(configfile=""):
    del configfile
    return doorpi.INSTANCE.config.save_config()
