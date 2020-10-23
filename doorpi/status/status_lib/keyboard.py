from typing import Any, Dict, Iterable

import doorpi.doorpi


def get(
        doorpi_obj: doorpi.doorpi.DoorPi,
        name: Iterable[str], value: Iterable[str],
        ) -> Dict[str, Any]:
    status_getters = {
        "name": lambda kb: "Keyboard handler",
        "input": lambda kb: {pin: kb.input(pin) for pin in value},
    }
    if not name:
        name = status_getters.keys()
    return {
        n: status_getters[n](doorpi_obj.keyboard)
        for n in name if n in status_getters}


def is_active(doorpi_object: doorpi.doorpi.DoorPi) -> bool:
    return bool(doorpi_object.keyboard)
