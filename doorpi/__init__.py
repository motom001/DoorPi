"""provide intercomstation to the doorstation by VoIP"""

import logging

__all__ = []

INSTANCE = None

logging.TRACE = 5
logging.addLevelName(logging.TRACE, "TRACE")


@logging.setLoggerClass
class DoorPiLogger(logging.getLoggerClass()):
    """Logger subclass that adds the TRACE level"""
    def trace(self, message, *args, **kw):
        """Logs with TRACE level"""
        if self.isEnabledFor(logging.TRACE):
            self._log(logging.TRACE, message, args, **kw)
