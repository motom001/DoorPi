"""Action that writes DoorPi status to a file: statusfile"""
import logging
import pathlib
from typing import Any, Mapping

import doorpi.actions
from doorpi.status.status_class import DoorPiStatus

from . import Action

LOGGER = logging.getLogger(__name__)


class StatusfileAction(Action):
    """Writes custom-formatted DoorPi status to a file."""

    def __init__(self, filename: str, *content: str) -> None:
        super().__init__()
        self.__filename = pathlib.Path(doorpi.INSTANCE.parse_string(filename))
        self.__content = ",".join(content).strip()

        self.__filename.parent.mkdir(parents=True, exist_ok=True)
        # create / truncate the file; also makes sure we have write permission
        self.__filename.open("w").close()

    def __call__(self, event_id: str, extra: Mapping[str, Any]) -> None:
        content = doorpi.INSTANCE.parse_string(self.__content)

        try:
            status = DoorPiStatus(doorpi.INSTANCE)
            content = content.replace(
                "!DOORPI_STATUS.json_beautified!", status.json_beautified
            )
            content = content.replace("!DOORPI_STATUS.json!", status.json)
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception(
                "[%s] Error fetching status information for file %s",
                event_id,
                self.__filename,
            )

        self.__filename.write_text(content)

    def __str__(self) -> str:
        return f"Write current status into {self.__filename}"

    def __repr__(self) -> str:
        return f"statusfile:{self.__filename},{self.__content.strip()}"
