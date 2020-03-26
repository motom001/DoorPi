def get(doorpi_obj, name, value):
    if not name: name = [""]
    if not value: value = [""]

    return_dict = {}
    for section_request in name:
        for section in doorpi_obj.config.get_sections(section_request):
            return_dict[section] = {}
            for value_request in value:
                return_dict[section].update(
                    {key: doorpi_obj.config.get_string(section, key)
                     for key in doorpi_obj.config.get_keys(section, value_request)})
            if not return_dict[section]:
                del return_dict[section]
    return return_dict


def is_active(doorpi_object):
    return bool(doorpi_object.config)
