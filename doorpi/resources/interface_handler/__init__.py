# -*- coding: utf-8 -*-

from main import DOORPI
import importlib
import os
from exceptions import *
logger = DOORPI.register_module(__name__, return_new_logger=True)


class InterfaceHandler:
    _interfaces = dict()

    @property
    def INSTALLED(self): return DOORPI.CONST.INTERFACES_AVAILABLE

    @property
    def ACTIVE(self): return self._interfaces.keys()

    def __init__(self):
        pass

    def start(self):
        logger.debug("start InterfaceHandler")

        DOORPI.events.register_events(__name__)

        DOORPI.CONST.INTERFACES_AVAILABLE = []
        interface_base_path = os.path.join(DOORPI.CONST.BASE_PATH, 'doorpi', 'plugins', 'interfaces')
        for root, sub_dirs, files in os.walk(interface_base_path):
            if len(sub_dirs) == 0:
                interface_name = root.replace(interface_base_path, "").replace(os.sep, ".")[1:]
                interface_doc = DOORPI.config.get_module_documentation_by_module_name(
                    DOORPI.CONST.INTERFACES_BASE_IMPORT_PATH + interface_name
                )
                if interface_doc is not None:
                    DOORPI.CONST.INTERFACES_AVAILABLE.append(interface_name)
                    logger.debug("- %s" % interface_name)

        logger.info("founded %s installed interfaces" % len(DOORPI.CONST.INTERFACES_AVAILABLE))

        for interface_name in DOORPI.config('/interfaces', default=[], function='keys'):
            self.load_interface('/interfaces/', interface_name)
        logger.debug('loaded %s interfaces', len(self._interfaces))

    def stop(self):
        logger.debug("stop InterfaceHandler")

    def get_interface_by_name(self, interface_name):
        if interface_name in self.ACTIVE:
            return self._interfaces[interface_name]
        else:
            return None

    def load_interface(self, config_path, interface_name):
        try:
            module_type = DOORPI.config(config_path + interface_name + '/type', None)
            if not module_type:
                raise InterfaceTypMissingException()
            if module_type not in DOORPI.CONST.INTERFACES_AVAILABLE:
                raise InterfaceTypNotAvailableException()
            if interface_name in self.ACTIVE:
                raise InterfaceNameAlreadyExistsException(interface_name)

            interface_object = importlib.import_module(
                DOORPI.CONST.INTERFACES_BASE_IMPORT_PATH + module_type).__interface__(
                name=interface_name,
                config_path=config_path + interface_name
            )

            self._interfaces[interface_name] = interface_object
            self._interfaces[interface_name].start()

        except Exception as exp:
            logger.exception('failed to load interface with error %s', exp)

    __call__ = get_interface_by_name
