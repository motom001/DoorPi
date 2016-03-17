# -*- coding: utf-8 -*-

from main import DOORPI
logger = DOORPI.register_module(__name__, return_new_logger = True)

from plugins.interfaces.hardware import HardwareInterfaceBaseClass

class FileSystemBasedInterface(HardwareInterfaceBaseClass):

    def __init__(self):
        pass

    def start(self, interface_id, config):
        logger.debug('[%s] start interface %s (type: %s)', interface_id, config['name'], config['type'])

    def stop(self):
        pass





__interface__ = FileSystemBasedInterface()
