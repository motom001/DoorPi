def get(doorpi_obj, name, value):
    return_dict = {}
    for section in name:
        try:
            view = doorpi_obj.config.view(section)
        except KeyError:
            pass
        else:
            return_dict[section] = {k: v for k, v in view.items() if k in value}
    return return_dict


def is_active(doorpi_object):
    return bool(doorpi_object.config)
