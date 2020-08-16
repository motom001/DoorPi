import operator


def get(doorpi_obj, name, value):
    del value
    status_getters = {
        "config_status": operator.attrgetter("config_status"),
        "session_ids": operator.attrgetter("sessions.session_ids"),
        "sessions": operator.attrgetter("sessions.sessions"),
        "running": lambda ws: bool(ws and ws.keep_running),
        "server_name": operator.attrgetter("server_name"),
        "server_port": operator.attrgetter("server_port"),
    }
    if not name:
        name = status_getters.keys()
    return {
        n: status_getters[n](doorpi_obj.webserver)
        for n in name if n in status_getters}


def is_active(doorpi_object):
    return bool(doorpi_object.webserver)
