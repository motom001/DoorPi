"""Actions related to logging: log"""
import logging
from typing import Any, Mapping

import doorpi

from . import Action, action

LOGGER = logging.getLogger(__name__)


@action("log")
class LogAction(Action):
    """Outputs a custom message to the log."""

    def __init__(self, *msg: str) -> None:
        super().__init__()
        self.__msg = ",".join(msg)

    def __call__(self, event_id: str, extra: Mapping[str, Any]) -> None:
        LOGGER.info(
            "[%s] %s", event_id, doorpi.INSTANCE.parse_string(self.__msg)
        )

    def __str__(self) -> str:
        return f"Log the message {self.__msg}"

    def __repr__(self) -> str:
        return f"log:{self.__msg}"
