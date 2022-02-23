#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import sys
import logging
import logging.handlers
import os
import pathlib

if __package__ is None:
    DIR = pathlib.Path(__file__).resolve().parent
    sys.path.insert(0, str(DIR.parent))
    __package__ = DIR.name

from doorpi import metadata
from doorpi import doorpi

TRACE_LEVEL = 5
LOG_FORMAT = '%(asctime)s [%(levelname)s]  \t[%(name)s] %(message)s'

logger = logging.getLogger(__name__)
log_level = logging.INFO


def add_trace_level():
    logging.addLevelName(TRACE_LEVEL, "TRACE")

    def trace(self, message, *args, **kws):
        if self.isEnabledFor(TRACE_LEVEL):
            self._log(TRACE_LEVEL, message, args, **kws)
    logging.Logger.trace = trace


def init_logger(arguments):
    add_trace_level()

    # set log level according to args (info = default, trace, debug)
    global log_level
    if '--debug' in arguments:
        log_level = logging.DEBUG
    elif '--trace' in arguments:
        log_level = TRACE_LEVEL

    # configure logger according to settings
    logging.basicConfig(level=log_level, format=LOG_FORMAT)
    return logging.getLogger(__name__)


def parse_arguments(argv):
    arg_parser = argparse.ArgumentParser(
        prog=argv[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=metadata.description,
        epilog=metadata.epilog)

    arg_parser.add_argument('-V', '--version',
                            action='version',
                            version='{0} {1}'.format(metadata.project, metadata.version))
    arg_parser.add_argument('--debug', action='store_true')
    arg_parser.add_argument('--trace', action='store_true')
    arg_parser.add_argument('--test', action='store_true')
    arg_parser.add_argument('-c', '--configfile',
                            help='configuration file for DoorPi',
                            dest='configfile')

    try:
        # if first argv is deamon control argv - interpret just the other argvs
        if len(sys.argv) > 1 and sys.argv[1] in ['start', 'stop', 'restart', 'status']:
            return arg_parser.parse_args(args=sys.argv[2:])
        else:
            return arg_parser.parse_args(args=sys.argv[1:])
    except IOError:
        print('EXCEPTION: configfile does not exist or is not readable')
        print('please refer to the DoorPi wiki for more information')
        print('<https://github.com/motom001/DoorPi/wiki>')
        raise SystemExit(1)


def files_preserve_by_path(*paths):

    from resource import getrlimit, RLIMIT_NOFILE

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


def main_as_daemon(argv):
    if argv[1] in ['reload']:
        print('not implemeted yet - use restart instead')
        return 1
    if argv[1] in ['stop']:
        parsed_arguments = None
    else:
        parsed_arguments = parse_arguments(argv)

    if not os.path.exists(metadata.log_folder):
        os.makedirs(metadata.log_folder)

    log_file = os.path.join(metadata.log_folder, "doorpi.log")
    logrotating = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=5000000,
        backupCount=10)

    global log_level
    logrotating.setLevel(log_level)
    logrotating.setFormatter(logging.Formatter(LOG_FORMAT))
    logging.getLogger('').addHandler(logrotating)

    print((metadata.epilog))

    from daemon import runner
    from daemon.runner import DaemonRunnerStartFailureError
    from daemon.runner import DaemonRunnerStopFailureError

    daemon_runner = runner.DaemonRunner(doorpi.DoorPi(parsed_arguments))
    # This ensures that the logger file handle does not get closed during daemonization
    daemon_runner.daemon_context.files_preserve = files_preserve_by_path(
        log_file)
    try:
        daemon_runner.do_action()
    except DaemonRunnerStopFailureError as ex:
        print(('stop DoorPi daemon failed - not running? (Message: {})').format(ex))
        return 1
    except DaemonRunnerStartFailureError as ex:
        print(('start DoorPi daemon failed - already running? (Message: {})').format(ex))
        return 1
    except Exception as ex:
        print(('Exception NameError: {}').format(ex))
    finally:
        doorpi.DoorPi().destroy()
    return 0


def main_as_application(argv):
    parsed_arguments = parse_arguments(argv)
    logger.info(metadata.epilog)
    logger.debug('loaded with arguments: %s', str(argv))

    try:
        doorpi.DoorPi(parsed_arguments).run()
    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt -> DoorPi will shutdown')
    except Exception as ex:
        logger.exception('Exception NameError: %s', ex)
    finally:
        doorpi.DoorPi().destroy()

    return 0


def entry_point():
    init_logger(sys.argv)

    """Zero-argument entry point for use with setuptools/distribute."""
    if len(sys.argv) > 1 and sys.argv[1] in ['start', 'stop', 'restart', 'reload']:
        raise SystemExit(main_as_daemon(sys.argv))
    else:
        raise SystemExit(main_as_application(sys.argv))


if __name__ == '__main__':
    entry_point()
