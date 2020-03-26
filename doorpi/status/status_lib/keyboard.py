def get(doorpi_obj, name, value):
    if not name: name = [""]
    if not value: value = [""]

    kb = doorpi_obj.keyboard
    status = {}

    for name_requested in name:
        if name_requested == "name":
            status["name"] = "Keyboard handler"
        elif name_requested == "input":
            status["input"] = {}
            for pin in value:
                status["input"][pin] = kb.input(pin)
        else: status[name_requested] = {"Error": "unsupported operation"}
    return status


def is_active(doorpi_object):
    return bool(doorpi_object.keyboard.name)
