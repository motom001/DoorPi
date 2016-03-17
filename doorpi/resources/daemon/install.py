# -*- coding: utf-8 -*-

from main import DOORPI
logger = DOORPI.register_module(__name__, return_new_logger = True)

import resources.external.pip as PIP
AUTOINSTALL_POSSIBLE = PIP.PIP_AVAILABLE

def install():
    logger.debug('install')
    from os import system as execute_commandline

    write_parsed_daemon_file()
    special_placeholder = get_special_placeholder()

    if execute_commandline(special_placeholder['DAEMON_INSTALL_COMMAND']) != 0:
        raise Exception('install daemon file failed')

    PIP.install('python-daemon')
    return True

def uninstall():
    logger.debug('uninstall')
    from platform import system
    from os import remove, system as execute_commandline

    special_placeholder = get_special_placeholder()

    try:    remove(special_placeholder['DAEMON_TARGET_FILENAME'])
    except: pass

    if execute_commandline(special_placeholder['DAEMON_UNINSTALL_COMMAND']) != 0:
        raise Exception('uninstall daemon file failed')

    #PIP.uninstall('python-daemon')
    return True

def reinstall():
    uninstall()
    install()
    return True

def update():
    return False

def get_special_placeholder():
    from platform import system
    return {
        'DAEMON_SOURCE_FILENAME':   main.parse_string(main.CONST.DAEMON_FILE[system()]['source']),
        'DAEMON_TARGET_FILENAME':   main.parse_string(main.CONST.DAEMON_FILE[system()]['target']),
        'DAEMON_INSTALL_COMMAND':   main.parse_string(main.CONST.DAEMON_FILE[system()]['install_command']),
        'DAEMON_UNINSTALL_COMMAND':   main.parse_string(main.CONST.DAEMON_FILE[system()]['uninstall_command']),
        'DAEMON_STDIN_PATH':        main.CONST.DAEMON_STDIN_PATH,
        'DAEMON_STDOUT_PATH':       main.CONST.DAEMON_STDOUT_PATH,
        'DAEMON_STDERR_PATH':       main.CONST.DAEMON_STDERR_PATH,
        'DAEMON_PIDFILE':           main.CONST.DAEMON_PIDFILE,
        'DAEMON_PIDFILE_TIMEOUT':   main.CONST.DAEMON_PIDFILE_TIMEOUT,
        'PROJECT':                  main.CONST.META.prog,
        'PROJECT_VERSION':          main.CONST.META.version,
        'PROJECT_DESCRIPTION':      main.CONST.META.description,
        'DAEMON_DEFAULT_ARGUMENTS': main.CONST.DAEMON_DEFAULT_ARGUMENTS
    }

def write_parsed_daemon_file():
    from os import stat as get_file_attributes, chmod
    from stat import S_IEXEC as ExecutableBit

    special_placeholder = get_special_placeholder()
    source_file = open(special_placeholder['DAEMON_SOURCE_FILENAME'], 'r')
    target_file = open(special_placeholder['DAEMON_TARGET_FILENAME'], 'w')

    logger.info("write example daemonfile from %s to %s and replace the placeholder inside the examplefile", special_placeholder['DAEMON_SOURCE_FILENAME'], special_placeholder['DAEMON_TARGET_FILENAME'])

    for single_line in source_file.readlines():
        target_file.write(main.parse_string(single_line, special_placeholder))
    source_file.close()
    target_file.close()

    logger.info("make the daemonfile %s executable", special_placeholder['DAEMON_TARGET_FILENAME'])
    chmod(special_placeholder['DAEMON_TARGET_FILENAME'], get_file_attributes(special_placeholder['DAEMON_TARGET_FILENAME']).st_mode | ExecutableBit)
    return special_placeholder['DAEMON_TARGET_FILENAME']

