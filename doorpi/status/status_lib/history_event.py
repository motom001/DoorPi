from typing import Any, Sequence

import doorpi.doorpi


def get(
    doorpi_obj: doorpi.doorpi.DoorPi,
    name: Sequence[str],
    value: Sequence[str],
) -> Any:
    try:
        filter_ = name[0]
    except IndexError:
        filter_ = ""

    try:
        max_count = int(value[0])
    except (IndexError, ValueError):
        max_count = 100

    return doorpi_obj.event_handler.log.get_event_log(max_count, filter_)


def is_active(doorpi_object: doorpi.doorpi.DoorPi) -> bool:
    return bool(doorpi_object.event_handler.log.get_event_log(1, ""))
