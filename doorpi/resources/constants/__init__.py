# -*- coding: utf-8 -*-

# section META from metadata
import resources.metadata as META

# section LOG
LOG_LEVEL = 'DEBUG'
LOG_FORMAT = '%(asctime)s [%(levelname)s]  \t[%(name)s] %(message)s'
LOG_DEFAULT_FILENAME = '/home/pi/dev/DoorPi3/log/doorpi.log'

BASE_PATH = ''

# section CONFIG
CONFIG_DEFAULT_FILENAME = '!BASE_PATH!/config/doorpi.json'
CONFIG_LAST_WORKING_FILENAME = '!BASE_PATH!/config/_last_working_doorpi_config.json'
CONFIG_PASSWORD_KEYS = ['password']

DOORPI_SHUTDOWN_TIMEOUT = 5
DOORPI_SHUTDOWN_TIMEOUT_CHECK_INTERVAL = 0.5

# section daemon
DAEMON_STDIN_PATH = '/dev/null'
DAEMON_STDOUT_PATH = '/dev/null'
DAEMON_STDERR_PATH = '/dev/null'
DAEMON_PIDFILE = '/home/pi/dev/DoorPi3/log/doorpi.pid'
DAEMON_PIDFILE_TIMEOUT = 5

DAEMON_FILE = {
    'source': '!BASE_PATH!/docs/service/linux.daemon.example',
    'target': '/etc/init.d/doorpi',
    'uninstall_command': 'update-rc.d doorpi remove',
    'install_command': 'update-rc.d doorpi defaults'
}

DAEMON_DEFAULT_ARGUMENTS = "--logfile "+LOG_DEFAULT_FILENAME

EVENTHANDLER_DB_TYP = 'sqlite'
EVENTHANDLER_DB_CONNECTIONSTRING = '!BASE_PATH!/conf/event_log.db'

USED_PYTHON_VERSION = ''

PIP_GENERAL_DEFAULT_ARGUMENTS = ['--disable-pip-version-check', '-q']
PIP_NOT_INSTALLED_ERROR = 'https://github.com/motom001/DoorPi/wiki/FAQ#wie-installiere-ich-pip'

HEART_BEAT_BASE_VALUE = 0.002
HEART_BEAT_REALTIME_VALUE = 0.2
HEART_BEAT_LEVEL_CRITICAL = 10
HEART_BEAT_LEVEL_ERROR = 25
HEART_BEAT_LEVEL_WARNING = 50
HEART_BEAT_LEVEL_INFO = 100
HEART_BEAT_LEVEL_DEBUG = 50000

DATETIME_PARTS = ['year', 'month', 'day', 'hour', 'minute', 'second']

MINUTE_RANGE = range(0, 60)
HOUR_RANGE = range(0, 23)
HANDLER_BASE_EVENTS = []
if len(HANDLER_BASE_EVENTS) == 0:
    for datetime_part in DATETIME_PARTS:
        HANDLER_BASE_EVENTS += ["OnTime%s" % datetime_part.capitalize()]

INTERFACES_AVAILABLE = []
INTERFACES_BASE_IMPORT_PATH = 'plugins.interfaces.'
INTERFACES_HARDWARE_DEFAULT_INPUT_EVENTS = ['OnInputActive', 'OnInputInactive', 'OnInputChange']
INTERFACES_HARDWARE_DEFAULT_OUTPUT_EVENTS = ['OnOutputActive', 'OnOutputInactive', 'OnOutputChange']
INTERFACES_HARDWARE_INCOMING_OUTPUT_EVENTS_HIGH = ['OnSetOutput', 'OnSetOutputHigh']
INTERFACES_HARDWARE_INCOMING_OUTPUT_EVENTS_LOW = ['OnSetOutputLow']

HIGH_LEVEL = ['1', 'high', 'on', 'true', True, 1]
LOW_LEVEL = ['0', 'low', 'off', 'false', False, 0]
