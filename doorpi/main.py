#!/usr/bin/env python3

import argparse
import sys
import logging
import logging.handlers
import os

from . import metadata
from . import doorpi

# Regular log format
LOG_FORMAT = "%(asctime)s [%(levelname)s]  \t[%(name)s] %(message)s"
# Format when logging to the journal
LOG_FORMAT_JOURNAL = "[%(levelname)s][%(name)s] %(message)s"

logger = logging.getLogger(__name__)

log_level = logging.INFO


def add_trace_level():
    def trace(self, message, *args, **kws):
        if self.isEnabledFor(logging.TRACE):
            self._log(logging.TRACE, message, args, **kws)
    logging.TRACE = 5
    logging.addLevelName(logging.TRACE, "TRACE")
    logging.Logger.trace = trace


def init_logger(args):
    add_trace_level()

    # check if we're connected to the journal
    journal = False
    expected_fd = os.environ.get("JOURNAL_STREAM", "").split(":")
    if len(expected_fd) == 2:
        stat = os.fstat(1)  # stdout
        try: journal = stat.st_dev == int(expected_fd[0]) and stat.st_ino == int(expected_fd[1])
        except ValueError: journal = False

    if args.logfile is None:
        logging.basicConfig(level=log_level, format=LOG_FORMAT_JOURNAL if journal else LOG_FORMAT)
    else:
        handler = logging.handlers.RotatingFileHandler(
            args.logfile, maxBytes=5_000_000, backupCount=10)
        logging.basicConfig(level=log_level, format=LOG_FORMAT, handlers=(handler,))

    if args.debug is not None:
        for lg in args.debug: logging.getLogger(lg).setLevel(logging.DEBUG)
    if args.trace is not None:
        for lg in args.trace: logging.getLogger(lg).setLevel(logging.TRACE)


def parse_arguments():
    arg_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=metadata.description,
        epilog=metadata.epilog
    )

    arg_parser.add_argument("-V", "--version", action="version",
                            version=f"{metadata.project} v{metadata.version}")
    arg_parser.add_argument("--debug", action="append", nargs="?", const="",
                            help="Enable debug logging (optionally on a specific component)")
    arg_parser.add_argument("--trace", action="append", nargs="?", const="",
                            help="Enable trace logging (optionally on a specific component)")
    arg_parser.add_argument("--test", action="store_true",
                            help="Enable test mode (exit after 10 seconds)")
    arg_parser.add_argument("--logfile", action="store", nargs=1,
                            help="Specify file to log into. If unspecified, log to stderr.")

    default_cfg = f"{sys.prefix if sys.prefix != '/usr' else ''}/etc/doorpi/doorpi.ini"
    arg_parser.add_argument("-c", "--configfile",
                            help=f"Specify configuration file to use (default: {default_cfg})",
                            default=default_cfg)

    return arg_parser.parse_args(args=sys.argv[1:])


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""

    args = parse_arguments()
    init_logger(args)
    logger.info(metadata.epilog)
    logger.debug("DoorPi starting with arguments: %s", args)

    instance = doorpi.DoorPi(args)
    try:
        instance.run()
    except BaseException as e:
        logger.error("*** UNCAUGHT EXCEPTION: %s: %s", e.__class__.__name__, str(e))
        logger.error("*** Attempting graceful shutdown...")
        raise
    finally:
        instance.destroy()


if __name__ == "__main__":
    entry_point()
