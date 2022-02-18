from typing import Any, Iterable

import doorpi.doorpi


def get(
    doorpi_obj: doorpi.doorpi.DoorPi,
    name: Iterable[str],
    value: Iterable[str],
) -> Any:
    return_dict = {}
    for section in name:
        try:
            view = doorpi_obj.config.view(section)
        except KeyError:
            pass
        else:
            return_dict[section] = {
                k: v for k, v in view.items() if k in value
            }
    return return_dict


def is_active(doorpi_object: doorpi.doorpi.DoorPi) -> bool:
    return bool(doorpi_object.config)
