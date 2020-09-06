"""provide intercomstation to the doorstation by VoIP"""

import logging
from typing import TYPE_CHECKING, List

__all__: List[str] = []

INSTANCE: "doorpi.DoorPi"

logging.TRACE = 5  # type: ignore
logging.addLevelName(logging.TRACE, "TRACE")  # type: ignore


class DoorPiLogger(logging.getLoggerClass()):  # type: ignore
    """Logger subclass that adds the TRACE level"""
    def trace(self, message, *args, **kw):
        """Logs with TRACE level"""
        if self.isEnabledFor(logging.TRACE):  # pragma: no cover # type: ignore
            self._log(logging.TRACE, message, args, **kw)


logging.setLoggerClass(DoorPiLogger)

if TYPE_CHECKING:
    from . import doorpi
else:
    INSTANCE = None
