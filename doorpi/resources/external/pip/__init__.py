# -*- coding: utf-8 -*-

from main import DOORPI
logger = DOORPI.register_module(__name__, return_new_logger = True)

class PipNotAvailableException(Exception): pass

try:
    import pip
    PIP_AVAILABLE = True
except ImportError as exp:
    logger.critical(DOORPI.CONST.PIP_NOT_INSTALLED_ERROR)
    PIP_AVAILABLE = False

def list_pip_modules():
    from pip.utils import get_installed_distributions
    return_array = []
    for line in get_installed_distributions():
        return_array.append(line.project_name)
    return return_array

def is_pip_modul_installed(package):
    return package in list_pip_modules()

def install(package):
    if not PIP_AVAILABLE: raise PipNotAvailableException()
    if is_pip_modul_installed(package): return True
    logger.info('try to install pip package %s', package)
    return pip.main(DOORPI.CONST.PIP_GENERAL_DEFAULT_ARGUMENTS + ['install', package])

def update(package):
    return False

def uninstall(package):
    if not PIP_AVAILABLE: raise PipNotAvailableException()
    if not is_pip_modul_installed(package): return True
    logger.warning('try to uninstall pip package %s', package)
    return pip.main(DOORPI.CONST.PIP_GENERAL_DEFAULT_ARGUMENTS + ['uninstall', 'y', package])
