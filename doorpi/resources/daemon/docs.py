# -*- coding: utf-8 -*-

from main import DOORPI

logger = DOORPI.register_module(__name__, return_new_logger=True)


def get_special_placeholder():
    from platform import system
    return {
        'DAEMON_SOURCE_FILENAME': DOORPI.parse_string(DOORPI.CONST.DAEMON_FILE['source']),
        'DAEMON_TARGET_FILENAME': DOORPI.parse_string(DOORPI.CONST.DAEMON_FILE['target']),
        'DAEMON_INSTALL_COMMAND': DOORPI.parse_string(DOORPI.CONST.DAEMON_FILE['install_command']),
        'DAEMON_UNINSTALL_COMMAND': DOORPI.parse_string(DOORPI.CONST.DAEMON_FILE['uninstall_command']),
        'DAEMON_STDIN_PATH': DOORPI.CONST.DAEMON_STDIN_PATH,
        'DAEMON_STDOUT_PATH': DOORPI.CONST.DAEMON_STDOUT_PATH,
        'DAEMON_STDERR_PATH': DOORPI.CONST.DAEMON_STDERR_PATH,
        'DAEMON_PIDFILE': DOORPI.CONST.DAEMON_PIDFILE,
        'DAEMON_PIDFILE_TIMEOUT': DOORPI.CONST.DAEMON_PIDFILE_TIMEOUT,
        'PROJECT': DOORPI.CONST.META.prog,
        'PROJECT_VERSION': DOORPI.CONST.META.version,
        'PROJECT_DESCRIPTION': DOORPI.CONST.META.description,
        'DAEMON_DEFAULT_ARGUMENTS': DOORPI.CONST.DAEMON_DEFAULT_ARGUMENTS
    }


def write_parsed_daemon_file():
    from os import stat as get_file_attributes, chmod
    from stat import S_IEXEC as ExecutableBit

    special_placeholder = get_special_placeholder()
    source_file = open(special_placeholder['DAEMON_SOURCE_FILENAME'], 'r')
    target_file = open(special_placeholder['DAEMON_TARGET_FILENAME'], 'w')

    logger.info("write example daemonfile from %s to %s and replace the placeholder inside the examplefile",
                special_placeholder['DAEMON_SOURCE_FILENAME'], special_placeholder['DAEMON_TARGET_FILENAME'])

    for single_line in source_file.readlines():
        target_file.write(DOORPI.parse_string(single_line, special_placeholder))
    source_file.close()
    target_file.close()

    logger.info("make the daemonfile %s executable", special_placeholder['DAEMON_TARGET_FILENAME'])
    chmod(special_placeholder['DAEMON_TARGET_FILENAME'],
          get_file_attributes(special_placeholder['DAEMON_TARGET_FILENAME']).st_mode | ExecutableBit)
    return special_placeholder['DAEMON_TARGET_FILENAME']


def remove_daemon_file():
    from os import remove
    special_placeholder = get_special_placeholder()
    logger.warning('remove daemon file %s', special_placeholder['DAEMON_TARGET_FILENAME'])
    remove(special_placeholder['DAEMON_TARGET_FILENAME'])
    return True


def register_daemon_file():
    from os import system as execute_commandline
    special_placeholder = get_special_placeholder()
    logger.info('register daemon file %s to os with %s', special_placeholder['DAEMON_TARGET_FILENAME'],
                special_placeholder['DAEMON_INSTALL_COMMAND'])
    if execute_commandline(special_placeholder['DAEMON_INSTALL_COMMAND']) != 0:
        raise Exception('register_daemon_file file failed')
    return True


def unregister_daemon_file():
    from os import system as execute_commandline
    special_placeholder = get_special_placeholder()
    logger.warning('unregister daemon file %s to os with %s', special_placeholder['DAEMON_TARGET_FILENAME'],
                   special_placeholder['DAEMON_INSTALL_COMMAND'])
    if execute_commandline(special_placeholder['DAEMON_UNINSTALL_COMMAND']) != 0:
        raise Exception('register_daemon_file file failed')
    return True


DOCUMENTATION = dict(
    fulfilled_with_one=False,
    text_description='''
A well-behaved Unix daemon process is tricky to get right, but the required steps are much the same for every daemon program.
A DaemonContext instance holds the behaviour and configured process environment for the program; use the instance as a context manager to enter a daemon state.
''',
    events=[
        # dict( name = 'Vorlage', description = '', parameter = [ dict( name = 'param1', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ) ]),
    ],
    configuration=[
        # dict( json_path = 'resources/event_handler/event_log/typ', type = 'string', default = 'sqllite', mandatory = False, description = 'Typ der Event_Hanler Datenbank (aktuell nur sqllite)'),
    ],
    auto_install=dict(
        available=True,
        install=[write_parsed_daemon_file, register_daemon_file],
        uninstall=[unregister_daemon_file, remove_daemon_file],
        update=[]
    ),
    libraries=dict(
        daemon=dict(
            mandatory=False,
            text_warning='only for unix',
            text_description='Library to implement a well-behaved Unix daemon process',
            text_installation='Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install=dict(
                standard=False,
                pip=['python-daemon']
            ),
            text_test='Der Status kann gestestet werden, in dem im Python-Interpreter <code>import daemon</code> eingeben wird.',
            text_configuration='Es ist keine Konfiguration vorgesehen.',
            configuration=[],
            text_links={
                'pypi.python.org': 'https://pypi.python.org/pypi/python-daemon/'
            }
        )
    )
)
