import logging
import doorpi
from pathlib import Path

from doorpi.actions import Action
from doorpi.status.status_class import DoorPiStatus


logger = logging.getLogger(__name__)


class StatusfileAction(Action):

    def __init__(self, filename, content):
        self.__filename = Path(doorpi.DoorPi().parse_string(filename))
        self.__content = content.strip() + "\n"

        self.__filename.parent.mkdir(parents=True, exist_ok=True)
        # create / truncate the file; also makes sure we have write permission
        self.__filename.open("w").close()

    def __call__(self, event_id, extra):
        content = doorpi.DoorPi().parse_string(self.__content)

        try:
            status = DoorPiStatus(doorpi.DoorPi())
            content = content.replace("!DOORPI_STATUS.json_beautified!", status.json_beautified)
            content = content.replace("!DOORPI_STATUS.json!", status.json)
        except Exception:
            logger.exception("[%s] Error fetching status information for file %s",
                             event_id, self.__filename)

        with self.__filename.open("w") as f:
            f.write(content)

    def __str__(self):
        return f"Write current status into {self.__filename}"

    def __repr__(self):
        return f"{__name__.split('.')[-1]}:{self.__filename},{self.__content.strip()}"


instantiate = StatusfileAction
