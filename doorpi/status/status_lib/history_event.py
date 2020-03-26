def get(doorpi_obj, name, value):
    try:
        filter_ = name[0]
    except IndexError:
        filter_ = ""

    try:
        max_count = int(value[0])
    except (IndexError, ValueError):
        max_count = 100

    return doorpi_obj.event_handler.db.get_event_log(max_count, filter_)


def is_active(doorpi_object):
    return bool(doorpi_object.event_handler.db.get_event_log_entries(1, ""))
