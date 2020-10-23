from typing import Any, Dict, Iterable

import doorpi.actions.snapshot
import doorpi.doorpi


def get(
    doorpi_obj: doorpi.doorpi.DoorPi,
    name: Iterable[str],
    value: Iterable[str],
) -> Dict[str, Any]:
    del doorpi_obj, name, value

    path = str(doorpi.actions.snapshot.SnapshotAction.get_base_path())
    files: Iterable[str] = map(
        str, doorpi.actions.snapshot.SnapshotAction.list_all()
    )
    # because path is added by webserver automatically
    if path.find("DoorPiWeb"):
        changedpath = path[path.find("DoorPiWeb") + len("DoorPiWeb") :]
        files = [f.replace(path, changedpath) for f in files]
    return dict.fromkeys(files, True)


def is_active(doorpi_obj: doorpi.doorpi.DoorPi) -> bool:
    del doorpi_obj
    return True
