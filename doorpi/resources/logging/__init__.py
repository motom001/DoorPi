# -*- coding: utf-8 -*-
from logging import Handler
import time


class DoorPiMemoryLog(Handler):
    _logs = []

    @property
    def log(self): return self._logs

    @property
    def log_formated(self):
        return map(self.format, self.log)

    def __init__(self):
        """
        Initialize the handler.
        """
        Handler.__init__(self)

    def reset(self):
        """
        reset the array.
        """
        self._logs = []

    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        try:
            self._logs.append(record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def init_own_logger(name):
    from logging import getLogger
    logger = getLogger(name)
    logger.debug("%s loaded", name)
    return logger
