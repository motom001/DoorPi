#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys
import logging
import logging.handlers
import os
import metadata
import doorpi
from resource import getrlimit, RLIMIT_NOFILE

TRACE_LEVEL = 5
LOG_FORMAT = '%(asctime)s [%(levelname)s]  \t[%(name)s] %(message)s'
DEFAULT_LOG_FILENAME = '/var/log/doorpi/doorpi.log'

logger = logging.getLogger(__name__)

log_level = logging.INFO

def add_trace_level():
    logging.addLevelName(TRACE_LEVEL, "TRACE")
    def trace(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        self._log(TRACE_LEVEL, message, args, **kws)
    logging.Logger.trace = trace


def init_logger(arguments):
    add_trace_level()

    global log_level
    if '--debug' in arguments: log_level = logging.DEBUG
    if '--trace' in arguments: log_level = TRACE_LEVEL

    logging.basicConfig(
        level = log_level,
        format = LOG_FORMAT
    #    datefmt = '%m/%d/%Y %I:%M:%S %p'
    )

    return logging.getLogger(__name__)



def parse_arguments(argv):
    arg_parser = argparse.ArgumentParser(
        prog=argv[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=metadata.description,
        epilog = metadata.epilog
    )

    arg_parser.add_argument(
        '-V', '--version',
        action='version',
        version='{0} {1}'.format(metadata.project, metadata.version)
    )
    arg_parser.add_argument('--debug', action="store_true")
    arg_parser.add_argument('--trace', action="store_true")
    arg_parser.add_argument(
        '--configfile',
        help='configfile for DoorPi - https://github.com/motom001/DoorPi/wiki for more help',
        type=file,
        dest='configfile',
        required = False
    )
    try:
        if  len(sys.argv) > 1 and sys.argv[1] in ['start', 'stop', 'restart', 'status']: # running as daemon? cut first argument
            return  arg_parser.parse_args(args=sys.argv[2:])
        else:
            return  arg_parser.parse_args(args=sys.argv[1:])
    except IOError:
        print "EXCEPTION: configfile does not exist or is not readable"
        print "please refer to the DoorPi wiki for more information "
        print "<https://github.com/motom001/DoorPi/wiki>"
        raise SystemExit(1)

def files_preserve_by_path(*paths):
    wanted=[]
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
    return [ fd for fd in xrange(fd_max) if fd_wanted(fd) ]

def get_status_from_doorpi(argv):
    try:
        print "called: %s" % argv
        import urllib2
        print urllib2.urlopen("http://127.0.0.1:8080/status?json&output=all").read()
    except Exception as ex:
        print "couln't get Status (Message: %s)" % ex
        return 1
    return 0

def main_as_daemon(argv):
    if argv[1] is 'reload':
        print 'not implemeted yet - use restart instead'
        return 1
    if argv[1] in ['stop']:
        parsed_arguments = None
    else:
        parsed_arguments = parse_arguments(argv)

    logrotating = logging.handlers.RotatingFileHandler(
          DEFAULT_LOG_FILENAME,
          maxBytes=50000,
          backupCount=10
    )
    global log_level
    logrotating.setLevel(log_level)
    logrotating.setFormatter(logging.Formatter(LOG_FORMAT))

    logging.getLogger('').addHandler(logrotating)

    print metadata.epilog

    from daemon import runner
    from daemon.runner import DaemonRunnerInvalidActionError
    from daemon.runner import DaemonRunnerStartFailureError
    from daemon.runner import DaemonRunnerStopFailureError

    daemon_runner = runner.DaemonRunner(doorpi.DoorPi(parsed_arguments))
    #This ensures that the logger file handle does not get closed during daemonization
    daemon_runner.daemon_context.files_preserve = files_preserve_by_path(DEFAULT_LOG_FILENAME)
    try:
        daemon_runner.do_action()
        logger.info('loaded with arguments: %s', str(argv))
    except DaemonRunnerStopFailureError as ex:
        print "can't stop DoorPi daemon - maybe it's not running? (Message: %s)" % ex
        return 1
    except DaemonRunnerStartFailureError as ex:
        print "can't start DoorPi daemon - maybe it's running already? (Message: %s)" % ex
        return 1
    except Exception as ex:
        print "Exception NameError: %s" % ex
    finally:
        doorpi.DoorPi().destroy()

    return 0

def main_as_application(argv):

    parsed_arguments = parse_arguments(argv)
    logger.info(metadata.epilog)
    logger.debug('loaded with arguments: %s', str(argv))

    try:                        doorpi.DoorPi(parsed_arguments).run()
    except KeyboardInterrupt:   logger.info("KeyboardInterrupt -> DoorPi will shutdown")
    except Exception as ex:     logger.exception("Exception NameError: %s", ex)
    finally:                    doorpi.DoorPi().destroy()

    return 0

def entry_point():
    if os.geteuid() != 0:
        print "DoorPi must run with sudo rights"
        raise SystemExit(1)

    """Zero-argument entry point for use with setuptools/distribute."""
    if len(sys.argv) > 1 and sys.argv[1] in ['status']:
        raise SystemExit(get_status_from_doorpi(sys.argv))
    elif len(sys.argv) > 1 and sys.argv[1] in ['start', 'stop', 'restart', 'reload']:
        raise SystemExit(main_as_daemon(sys.argv))
    else:
        raise SystemExit(main_as_application(sys.argv))

if __name__ == '__main__':
    init_logger(sys.argv)
    entry_point()
