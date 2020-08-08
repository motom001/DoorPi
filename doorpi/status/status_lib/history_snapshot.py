from doorpi.actions.snapshot import SnapshotAction


def get(doorpi_obj, name, value):
    del doorpi_obj, name, value

    path = str(SnapshotAction.get_base_path())
    files = SnapshotAction.list_all()
    # because path is added by webserver automatically
    if path.find("DoorPiWeb"):
        changedpath = path[path.find("DoorPiWeb") + len("DoorPiWeb"):]
        files = [f.replace(path, changedpath) for f in files]
    return files
