#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
import logging
import logging.handlers
#----------
import metadata
import doorpi

TRACE_LEVEL = 5
LOG_FORMAT = '%(asctime)s [%(levelname)s]  \t[%(name)s] %(message)s'
DEFAULT_LOG_FILENAME = '/var/log/doorpi/doorpi.log'

def add_trace_level():
    logging.addLevelName(TRACE_LEVEL, "TRACE")
    def trace(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        self._log(TRACE_LEVEL, message, args, **kws)
    logging.Logger.trace = trace

def init_logger():
    add_trace_level()
    logging.basicConfig(
        filename = DEFAULT_LOG_FILENAME,
        level = TRACE_LEVEL,
        format = LOG_FORMAT
    #    datefmt = '%m/%d/%Y %I:%M:%S %p'
    )
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(TRACE_LEVEL)
    console.setFormatter(logging.Formatter(LOG_FORMAT))

    logrotating = logging.handlers.RotatingFileHandler(
          DEFAULT_LOG_FILENAME,
          maxBytes=25000,
          backupCount=5
    )

    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    logging.getLogger('').addHandler(logrotating)

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

    arg_parser.add_argument(
        '--configfile',
        help='configfile for DoorPi',
        type=file,
        dest='configfile',
        required = True
    )

    if  len(sys.argv) > 1 and sys.argv[1] in ['start', 'stop', 'restart', 'status']: # running as daemon? cut first argument
        return  arg_parser.parse_args(args=sys.argv[2:])
    else:
        return  arg_parser.parse_args(args=sys.argv[1:])

def main_as_daemon(argv):
    if sys.argv[1] in ['status']:
        print 'Status: '
        return 0
    if sys.argv[1] is 'reload':
        print 'not implemeted now - use restart instead'
        return 1

    parsed_arguments = parse_arguments(argv)

    logger.info(metadata.epilog)
    logger.debug('loaded with arguments: %s', str(argv))

    from daemon import runner
    daemon_runner = runner.DaemonRunner(doorpi.DoorPi(parsed_arguments))
    #This ensures that the logger file handle does not get closed during daemonization
    #daemon_runner.daemon_context.files_preserve=[log_rotating.stream]
    try:                        daemon_runner.do_action()
    except Exception as ex:     logger.exception("Exception NameError: %s", ex)
    finally:                    doorpi.DoorPi().destroy()

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
    """Zero-argument entry point for use with setuptools/distribute."""
    if  len(sys.argv) > 1 and sys.argv[1] in ['start', 'stop', 'restart', 'status', 'reload']:
        raise SystemExit(main_as_daemon(sys.argv))
    else:
        raise SystemExit(main_as_application(sys.argv))

if __name__ == '__main__':
    logger = init_logger()
    entry_point()
