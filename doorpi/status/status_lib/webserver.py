import operator
from typing import Any, Callable, Dict, Iterable

import doorpi.doorpi


def get(
    doorpi_obj: doorpi.doorpi.DoorPi,
    name: Iterable[str],
    value: Iterable[str],
) -> Dict[str, Any]:
    del value
    status_getters: Dict[str, Callable[[doorpi.web.DoorPiWeb], Any]] = {
        "config_status": lambda _: {"infos": [], "warnings": [], "errors": []},
        "session_ids": lambda ws: list(ws.sessions.sessions),
        "sessions": operator.attrgetter("sessions.sessions"),
        "running": bool,
        "server_name": operator.attrgetter("server_name"),
        "server_port": operator.attrgetter("server_port"),
    }
    if not name:
        name = status_getters.keys()
    if doorpi_obj.webserver is None:
        return dict.fromkeys(name, None)
    else:
        return {
            n: status_getters[n](doorpi_obj.webserver)
            for n in name
            if n in status_getters
        }


def is_active(doorpi_object: doorpi.doorpi.DoorPi) -> bool:
    return bool(doorpi_object.webserver)
