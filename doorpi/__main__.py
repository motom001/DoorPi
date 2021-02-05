#!/usr/bin/env python3
"""The application launcher module."""
import argparse
import logging
import logging.handlers
import os
import sys

from doorpi import doorpi, metadata

# Regular log format
LOG_FORMAT = "%(asctime)s [%(levelname)s]  \t[%(name)s] %(message)s"
# Format when logging to the journal
LOG_FORMAT_JOURNAL = "[%(levelname)s][%(name)s] %(message)s"

LOGGER = logging.getLogger(__name__)

LOG_LEVEL = logging.INFO


def init_logger(args: argparse.Namespace) -> None:
    """Initializes the logging module with DoorPi settings."""
    # check if we're connected to the journal
    journal = False
    expected_fd = os.environ.get("JOURNAL_STREAM", "").split(":")
    if len(expected_fd) == 2:
        stat = os.fstat(1)  # stdout
        try:
            journal = stat.st_dev == int(
                expected_fd[0]
            ) and stat.st_ino == int(expected_fd[1])
        except ValueError:
            journal = False

    if args.logfile is None:
        logging.basicConfig(
            level=LOG_LEVEL,
            format=LOG_FORMAT_JOURNAL if journal else LOG_FORMAT,
        )
    else:
        handler = logging.handlers.RotatingFileHandler(
            args.logfile, maxBytes=5_000_000, backupCount=10
        )
        logging.basicConfig(
            level=LOG_LEVEL, format=LOG_FORMAT, handlers=(handler,)
        )

    if args.debug is not None:
        for lg in args.debug:
            logging.getLogger(lg).setLevel(logging.DEBUG)
    if args.trace is not None:
        for lg in args.trace:
            logging.getLogger(lg).setLevel(
                logging.TRACE  # type: ignore[attr-defined]
            )


def parse_arguments() -> argparse.Namespace:
    """Parses command line arguments."""
    dpmeta = metadata.distribution.metadata
    arg_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=dpmeta["Summary"],
        epilog=metadata.epilog,
    )

    arg_parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"DoorPi v{dpmeta['Version']}",
    )
    arg_parser.add_argument(
        "--debug",
        action="append",
        nargs="?",
        const="",
        help="Enable debug logging (optionally on a specific component)",
    )
    arg_parser.add_argument(
        "--trace",
        action="append",
        nargs="?",
        const="",
        help="Enable trace logging (optionally on a specific component)",
    )
    arg_parser.add_argument(
        "--test",
        action="store_true",
        help="Enable test mode (exit after 10 seconds)",
    )
    arg_parser.add_argument(
        "--logfile",
        action="store",
        nargs=1,
        help="Specify file to log into. If unspecified, log to stderr.",
    )

    default_cfg = "/".join(
        (sys.prefix if sys.prefix != "/usr" else "", "etc/doorpi/doorpi.ini")
    )
    arg_parser.add_argument(
        "-c",
        "--configfile",
        default=default_cfg,
        help=f"Specify configuration file to use (default: {default_cfg})",
    )

    return arg_parser.parse_args(args=sys.argv[1:])


def main() -> None:
    """Run DoorPi as standalone service"""
    args = parse_arguments()
    init_logger(args)
    LOGGER.info(metadata.epilog)
    LOGGER.debug("DoorPi starting with arguments: %s", args)

    instance = doorpi.DoorPi(args)
    del args
    try:
        os.chdir(instance.base_path)
        instance.prepare()
    except BaseException as err:
        LOGGER.error("*** An error occured while preparing to start")
        raise

    try:
        instance.run()
    except BaseException as err:
        LOGGER.error("*** UNCAUGHT EXCEPTION: %s: %s", type(err).__name__, err)
        LOGGER.error("*** Attempting graceful shutdown...")
        raise
    finally:
        instance.destroy()


if __name__ == "__main__":
    main()
