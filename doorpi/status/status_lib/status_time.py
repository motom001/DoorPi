import datetime
from typing import Iterable

import doorpi.doorpi


def get(
    doorpi_obj: doorpi.doorpi.DoorPi,
    name: Iterable[str],
    value: Iterable[str],
) -> str:
    del doorpi_obj, name, value
    return str(datetime.datetime.now())


def is_active(doorpi_object: doorpi.doorpi.DoorPi) -> bool:
    del doorpi_object
    return True
