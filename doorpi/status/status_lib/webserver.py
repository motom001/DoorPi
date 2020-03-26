def get(doorpi_obj, name, value):
    del value
    if not name: name = [""]

    webserver = doorpi_obj.webserver

    status = {}
    for name_requested in name:
        if name_requested in "config_status":
            status["config_status"] = webserver.config_status

        if name_requested in "session_ids":
            status["session_ids"] = webserver.sessions.session_ids

        if name_requested in "sessions":
            status["sessions"] = webserver.sessions.sessions

        if name_requested in "running":
            status["running"] = bool(webserver and webserver.keep_running)

        if name_requested in "server_name":
            status["server_name"] = webserver.server_name

        if name_requested in "server_port":
            status["server_port"] = webserver.server_port

    return status


def is_active(doorpi_object):
    return bool(doorpi_object.webserver)
