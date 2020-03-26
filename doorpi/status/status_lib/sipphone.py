def get(doorpi_obj, name, value):
    del value

    sipphone = doorpi_obj.sipphone
    status = {}

    while name:
        cur_name = name.pop()
        if cur_name == "name":
            status[cur_name] = sipphone.get_name()
        elif cur_name == "current_call":
            status[cur_name] = sipphone.dump_call()
        else:
            status[cur_name] = {"Error": f"Unknown name {cur_name!r}"}
    return status


def is_active(doorpi_object):
    return bool(doorpi_object.sipphone)
