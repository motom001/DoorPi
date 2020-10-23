"""provide intercomstation to the doorstation by VoIP"""

import logging
from typing import TYPE_CHECKING, Any, List

__all__: List[str] = []

INSTANCE: "doorpi.DoorPi"

logging.TRACE = 5  # type: ignore
logging.addLevelName(logging.TRACE, "TRACE")  # type: ignore


class DoorPiLogger(logging.getLoggerClass()):  # type: ignore
    """Logger subclass that adds the TRACE level"""
    def trace(self, message: str, *args: Any, **kw: Any) -> None:
        """Logs with TRACE level"""
        if self.isEnabledFor(logging.TRACE):  # type: ignore # pragma: no cover
            self._log(logging.TRACE, message, args, **kw)  # type: ignore


logging.setLoggerClass(DoorPiLogger)

if TYPE_CHECKING:  # pragma: no cover
    from . import doorpi
else:
    INSTANCE = None
