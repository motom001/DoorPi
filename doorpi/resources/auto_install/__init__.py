# -*- coding: utf-8 -*-

from main import DOORPI
logger = DOORPI.register_module(__name__, return_new_logger = True)

import importlib
import resources.external.pip as pip
import resources.functions.json as json_help


def update(module_name):    return execute_autoinstall_functions(module_name, 'update')

def uninstall(module_name): return execute_autoinstall_functions(module_name, 'uninstall')

def autoinstall_available(module_name):
    try:    return json_help.get_by_json_path(importlib.import_module(module_name+'.docs').DOCUMENTATION, 'auto_install/available', False)
    except: return False

def install(module_name):
    if not autoinstall_available(module_name):
        logger.info('no autoinstall for %s available', module_name)
        return False

    module_documentation = importlib.import_module(module_name+'.docs').DOCUMENTATION
    for library_name, library_object in list(json_help.get_by_json_path(module_documentation, 'libraries', dict()).items()):
        if json_help.get_by_json_path(library_object, 'auto_install/standard', False): continue
        for needed_pip_modul in json_help.get_by_json_path(library_object, 'auto_install/pip', []):
            if json_help.get_by_json_path(library_object, 'mandatory', False): continue
            try:                        pip.install(needed_pip_modul)
            except Exception as exp:
                logger.exception('failed to install pip module "%s" for module %s with error %s', needed_pip_modul, module_name, exp)
                return False

    return execute_autoinstall_functions(module_name, 'install')

def execute_autoinstall_functions(module_name, modus_name):
    module_documentation = importlib.import_module(module_name+'.docs').DOCUMENTATION
    for uninstall_function in json_help.get_by_json_path(module_documentation, 'auto_install/'+modus_name, []):
        try:
            uninstall_function()
        except Exception as exp:
            logger.exception('failed to execute %s function %s for module %s with error %s', modus_name, uninstall_function, module_name, exp)
            return False
    return True
