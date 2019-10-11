#!/usr/bin/env python3

import argparse
import sys
import logging
import logging.handlers
import os

from . import metadata
from . import doorpi
from resource import getrlimit, RLIMIT_NOFILE

TRACE_LEVEL = 5

# Regular log format
LOG_FORMAT = "%(asctime)s [%(levelname)s]  \t[%(name)s] %(message)s"
# Format when logging to the journal
LOG_FORMAT_JOURNAL = "[%(levelname)s][%(name)s] %(message)s"

logger = logging.getLogger(__name__)

log_level = logging.INFO


def add_trace_level():
    logging.addLevelName(TRACE_LEVEL, "TRACE")

    def trace(self, message, *args, **kws):
        if self.isEnabledFor(TRACE_LEVEL):
            self._log(TRACE_LEVEL, message, args, **kws)

    logging.Logger.trace = trace


def init_logger(args):
    add_trace_level()

    global log_level
    if args.debug: log_level = logging.DEBUG
    if args.trace: log_level = TRACE_LEVEL

    # check if we're connected to the journal
    journal = False
    expected_fd = os.environ.get("JOURNAL_STREAM", "").split(":")
    if len(expected_fd) == 2:
        stat = os.fstat(1)  # stdout
        try: journal = stat.st_dev == int(expected_fd[0]) and stat.st_ino == int(expected_fd[1])
        except ValueError: journal = False

    logging.basicConfig(level=log_level, format=LOG_FORMAT_JOURNAL if journal else LOG_FORMAT)


def parse_arguments():
    arg_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=metadata.description,
        epilog=metadata.epilog
    )

    arg_parser.add_argument("-V", "--version", action="version",
                            version=f"{metadata.project} v{metadata.version}")
    arg_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    arg_parser.add_argument("--trace", action="store_true", help="Enable trace logging")
    arg_parser.add_argument("--test", action="store_true",
                            help="Enable test mode (exit after 10 seconds)")

    default_cfg = f"{sys.prefix if sys.prefix != '/usr' else ''}/etc/doorpi/doorpi.ini"
    arg_parser.add_argument("-c", "--configfile",
                            help=f"Specify configuration file to use (default: {default_cfg})",
                            default=default_cfg)

    if len(sys.argv) > 1 and sys.argv[1] in ['start', 'stop', 'status']:
        return (sys.argv[1], arg_parser.parse_args(args=sys.argv[2:]))
    else:
        return (None, arg_parser.parse_args(args=sys.argv[1:]))


def files_preserve_by_path(*paths):
    wanted = []
    for path in paths:
        fd = os.open(path, os.O_RDONLY)
        try:
            wanted.append(os.fstat(fd)[1:3])
        finally:
            os.close(fd)

    def fd_wanted(fd):
        try:
            return os.fstat(fd)[1:3] in wanted
        except OSError:
            return False

    fd_max = getrlimit(RLIMIT_NOFILE)[1]
    return [fd for fd in range(fd_max) if fd_wanted(fd)]


def main_as_daemon(action, args):
    if action == "stop":
        args = None

    if not os.path.exists(metadata.log_folder):
        os.makedirs(metadata.log_folder)

    log_file = os.path.join(metadata.log_folder, "doorpi.log")
    logrotating = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5000000,
        backupCount=10
    )
    global log_level
    logrotating.setLevel(log_level)
    logrotating.setFormatter(logging.Formatter(LOG_FORMAT))

    logging.getLogger('').addHandler(logrotating)

    print((metadata.epilog))

    from daemon import runner
    from daemon.runner import DaemonRunnerInvalidActionError
    from daemon.runner import DaemonRunnerStartFailureError
    from daemon.runner import DaemonRunnerStopFailureError

    daemon_runner = runner.DaemonRunner(doorpi.DoorPi(args))
    # This ensures that the logger file handle does not get closed during daemonization
    daemon_runner.daemon_context.files_preserve = files_preserve_by_path(log_file)
    try:
        daemon_runner.do_action()
    except DaemonRunnerStopFailureError as ex:
        print(("can't stop DoorPi daemon - maybe it's not running? (Message: %s)" % ex))
        return 1
    except DaemonRunnerStartFailureError as ex:
        print(("can't start DoorPi daemon - maybe it's running already? (Message: %s)" % ex))
        return 1
    except Exception as ex:
        print(("*** UNCAUGHT EXCEPTION: %s" % ex))
        raise
    finally:
        doorpi.DoorPi().destroy()
    return 0


def main_as_application(args):
    logger.info(metadata.epilog)
    logger.debug('loaded with arguments: %s', args)

    try: doorpi.DoorPi(args).run()
    except KeyboardInterrupt: logger.info("KeyboardInterrupt -> DoorPi will shutdown")
    except Exception as ex:
        logger.exception("*** UNCAUGHT EXCEPTION: %s", ex)
        raise
    finally: doorpi.DoorPi().destroy()

    return 0


def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""

    action, args = parse_arguments()
    init_logger(args)

    if action is None:
        raise SystemExit(main_as_application(args))
    elif action == "status":
        raise SystemExit(get_status_from_doorpi(args))
    else:
        raise SystemExit(main_as_daemon(action, args))


if __name__ == '__main__':
    entry_point()
