import operator


def get(doorpi_obj, name, value):
    del value
    status_getters = {
        "name": operator.methodcaller("get_name"),
        "current_call": operator.methodcaller("dump_call"),
    }
    return {n: status_getters[n](doorpi_obj.sipphone) for n in name}


def is_active(doorpi_object):
    return bool(doorpi_object.sipphone)
