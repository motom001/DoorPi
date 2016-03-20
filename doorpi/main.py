#!/usr/bin/python
# -*- coding: utf-8 -*-

# system modules
import os
import platform
import sys
import argparse
import signal
import logging
import logging.handlers
import gettext

# self-import to prevent endless imports later
import main

# doorpi modules and doorpi itself
import resources.constants as CONST
from resources.singleton import Singleton
from resources.core import DoorPi, CorruptConfigFileException
from resources.logging import init_own_logger
try:
    from daemonize import Daemonize
except ImportError:
    Daemonize = None

logging.basicConfig(level=logging.DEBUG, format=CONST.LOG_FORMAT)
logger = init_own_logger(__name__)

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOORPI = Singleton(DoorPi)
gettext.install(
    domain='doorpi',
    localedir=os.path.join(BASE_PATH, 'doorpi', 'locale'),
    unicode=True
)
LAST_EXCEPTION = None


def parse_string(raw_string, kwargs=None):
    var_dict = globals()
    if kwargs:
        var_dict.update(kwargs)
    for var in var_dict:
        try:
            raw_string = raw_string.replace('!' + var + '!', var_dict[var])
        except:
            pass
    return raw_string


def create_daemon_file(daemon_file_template, daemon_file_target):
    logger.info(_("start to create daemon file now..."))
    with open(daemon_file_target, "w") as daemon_file:
        with open(daemon_file_template, "r") as daemon_template:
            for line in daemon_template.readlines():
                daemon_file.write(
                    parse_string(
                        line,
                        CONST.META.__dict__
                    )
                )
    logger.info(_("finished writing - now set mod to 0755"))
    os.chmod(daemon_file_target, 0777)
    logger.info(_("finished create daemon file"))
    return True


def entry_point():
    print(CONST.META.epilog)

    CONST.BASE_PATH = BASE_PATH
    CONST.USED_PYTHON_VERSION = "%s.%s" % (sys.version_info.major, sys.version_info.minor)

    possible_log_levels = map(logging.getLevelName, range(0, 51, 10))
    possible_daemon_commands = ['start', 'stop']

    parser = argparse.ArgumentParser(description=' - '.join([CONST.META.prog, CONST.META.project]))
    parser.add_argument("daemon", default='NONE', choices=possible_daemon_commands + ['NONE'],
                        help=_("doorpi parameter description daemon"), nargs='?')
    parser.add_argument('-c', '--configfile', default=CONST.CONFIG_DEFAULT_FILENAME, dest="config_file",
                        help=_("doorpi parameter description configfile"))
    parser.add_argument('--log_level', default=CONST.LOG_LEVEL, action='store', dest="log_level",
                        choices=possible_log_levels, help=_("doorpi parameter description log_level"))
    parser.add_argument('--logfile', default=CONST.LOG_DEFAULT_FILENAME, dest="log_file",
                        help=_("doorpi parameter description logfile"))
    parser.add_argument("--logfile_level", default=CONST.LOG_LEVEL, action="store", dest="logfile_level",
                        choices=possible_log_levels, help=_("doorpi parameter description logfile_level"))
    parser.add_argument("--logfile_maxBytes", default=5000000, dest="logfile_max_bytes", type=int,
                        help=_("doorpi parameter description logfile_maxBytes"))
    parser.add_argument("--logfile_maxFiles", default=10, dest="logfile_max_files", type=int,
                        help=_("doorpi parameter description logfile_maxFiles"))
    parser.add_argument("--skip_sudo_check", default=False, action="store_true", dest="skip_sudo_check",
                        help=_("doorpi parameter description skip_sudo_check"))
    parser.add_argument("--install_daemon", default=False, action="store_true", dest="install_daemon",
                        help=_("doorpi parameter description install_daemon"))
    parser.add_argument("--use_last_known_config", default=False, action="store_true", dest="use_last_known_config",
                        help=_("doorpi parameter description use_last_known_config"))
    parser.add_argument("--foreground_daemon", default=False, action="store_true", dest="foreground_daemon",
                        help=_("doorpi parameter description foreground_daemon"))
    parser.add_argument("--create_parsed_docs", default=False, action="store_true", dest="create_parsed_docs",
                        help=_("doorpi parameter description create_parsed_docs"))
    parser.add_argument("--test_mode", default=False, action="store_true", dest="test_mode",
                        help=_("doorpi parameter description test_mode"))
    args = parser.parse_args()

    if os.geteuid() != 0 and args.skip_sudo_check is False:
        raise SystemExit(
            _("DoorPi must run with sudo rights - maybe use --skip_sudo_check to skip this check")
        )

    CONST.LOG_LEVEL = args.log_level
    global_logger = logging.getLogger('')
    global_logger.setLevel(CONST.LOG_LEVEL)

    if args.install_daemon:
        if os.name == 'posix':
            daemon_file_template = os.path.join(BASE_PATH, 'doorpi', 'docs', 'linux.daemon.tpl')
            return create_daemon_file(
                daemon_file_template,
                CONST.META.daemon_file
            )
        else:
            return "DoorPi Error 1001 - unsupported os"

    DOORPI.prepare(args)
    DOORPI.logger.setLevel(CONST.LOG_LEVEL)
    DOORPI.logger.setFormatter(logging.Formatter(CONST.LOG_FORMAT))
    global_logger.addHandler(DOORPI.logger)

    daemon_args = dict(
        app=CONST.META.package,
        pid=parse_string(CONST.DAEMON_PIDFILE),
        action=DOORPI.start,
        verbose=True,
        chdir=parse_string('!BASE_PATH!'),
        foreground=args.foreground_daemon
    )

    if args.log_file:
        try:
            args.log_file = parse_string(args.log_file)
            if not os.path.exists(os.path.dirname(args.log_file)):
                os.makedirs(os.path.dirname(args.log_file))
            log_rotating = logging.handlers.RotatingFileHandler(
                args.log_file,
                maxBytes=args.logfile_max_bytes,
                backupCount=args.logfile_max_files
            )
            log_rotating.setLevel(args.logfile_level)
            log_rotating.setFormatter(logging.Formatter(CONST.LOG_FORMAT))
            logging.getLogger('').addHandler(log_rotating)
            daemon_args.update(dict(keep_fds=[log_rotating.stream.fileno()]))
        except IOError as exp:
            logging.exception(_("Managed exception while open logfile %s") % exp)

    logger = init_own_logger(__name__)
    logger.debug(_('loaded with arguments: %s'), str(args))

    doorpi_start_function = DOORPI.start

    if args.daemon.lower() == "stop":
        with open(daemon_args['pid'], "r") as pid_file:
            daemon_pid = int(pid_file.readline())
        logger.info(_("send SIGTERM to DoorPi with pi %s") % daemon_pid)
        os.kill(daemon_pid, signal.SIGTERM)
        doorpi_start_function = None
    elif Daemonize and args.daemon.lower() == "start":
        doorpi_start_function = Daemonize(**daemon_args).start

    try:
        if doorpi_start_function:
            doorpi_start_function()
    except KeyboardInterrupt:
        logger.info(_("KeyboardInterrupt -> DoorPi will shutdown"))
    except CorruptConfigFileException as ex:
        logger.exception(_("CorruptConfigFileException: %s"), ex)
    except Exception as ex:
        logger.exception(_("Exception: %s"), ex)
    finally:
        DOORPI.stop()

    logger.info(_('main finished'))

if __name__ == '__main__':
    raise SystemExit(entry_point())
