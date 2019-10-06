import datetime
import logging
import pathlib

import doorpi
from . import Action


logger = logging.getLogger(__name__)
DOORPI_SECTION = 'DoorPi'


class SnapshotAction(Action):

    @classmethod
    def cleanup(cls):
        keep = doorpi.DoorPi().config.get_int(DOORPI_SECTION, "snapshot_keep")
        if keep <= 0: return
        files = cls._list_all()
        for f in files[0:-keep]:
            try:
                logger.info("Deleting old snapshot %s", f)
                f.unlink()
            except OSError: logger.exception("Could not clean up snapshot %s", f.name)

    @staticmethod
    def get_base_path():
        path = doorpi.DoorPi().config.get_string_parsed(DOORPI_SECTION, "snapshot_path")
        if not path: raise ValueError("snapshot_path must not be empty")
        path = pathlib.Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_next_path(cls):
        p = cls.get_base_path() / datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.jpg")
        doorpi.DoorPi().config.set_value(DOORPI_SECTION, "last_snapshot", str(p))
        return p

    @classmethod
    def _list_all(cls):
        files = [f for f in cls.get_base_path().iterdir() if f.is_file()]
        files.sort()
        return files


class URLSnapshotAction(SnapshotAction):

    def __init__(self, url):
        self.__url = url

    def __call__(self, event_id, extra):
        import requests

        r = requests.get(self.__url, stream=True)
        with open(self.get_next_path(), "wb") as f:
            for chunk in r.iter_content(1048576):  # 1 MiB chunks
                f.write(chunk)

        self.cleanup()

    def __str__(self):
        return f"Save the image from {self.__url} as snapshot"

    def __repr__(self):
        return f"{__name__.split('.')[-1]}:{self.__url}"


class PicamSnapshotAction(SnapshotAction):

    def __init__(self):
        # Make sure picamera is importable
        import picamera

    def __call__(self, event_id, extra):
        import picamera

        with picamera.PiCamera() as cam:
            cam.resolution = (1024, 768)
            cam.capture(self.get_next_path())

        self.cleanup()

    def __str__(self):
        return f"Take a snapshot from the Pi Camera"

    def __repr__(self):
        return f"{__name__.split('.')[-1]}"


def instantiate(url=None):
    if url is not None: return URLSnapshotAction(url)
    else: return PicamSnapshotAction()
