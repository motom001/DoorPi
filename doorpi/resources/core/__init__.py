# -*- coding: utf-8 -*-
from resources.logging import DoorPiMemoryLog, init_own_logger
import time
import os
import string
import random
import main

logger = init_own_logger("resources.core")


class CorruptConfigFileException(Exception): pass


class DoorPi(object):
    _instance = None
    _arguments = None
    _modules = dict()

    _destroy = False
    _prepared = False

    _logger = None
    _config_handler = None
    _event_handler = None
    _interface_handler = None

    _start_as_daemon = True
    _core_documentation = None

    @property
    def logger(self):
        return self._logger

    @property
    def config(self):
        return self._config_handler

    @property
    def events(self):
        return self._event_handler

    @property
    def interfaces(self):
        return self._interface_handler

    @property
    def arguments(self):
        return self._arguments

    @property
    def CONST(self):
        return main.CONST

    @property
    def libraries(self):
        return {'libraries': []} if self._core_documentation is None else self._core_documentation['libraries']

    @property
    def modules_destroyed(self):
        if self.events is None: return True
        return self.events.idle

    @staticmethod
    def parse_string(raw_string, kwargs=None):
        return main.parse_string(raw_string, kwargs)

    @staticmethod
    def generate_id(size=6, chars=string.ascii_uppercase + string.digits, prefix='', postfix=''):
        return prefix + ''.join(random.choice(chars) for _ in range(size)) + postfix

    def __init__(self, ):
        pass

    def restart(self):
        logger.debug('restart')
        self.stop()
        self.__init__()
        self.start()

    def prepare(self, arguments):
        logger = init_own_logger(__name__)

        if arguments:
            self._arguments = arguments

        if not self._logger:
            logger.debug('set new logger DoorPiMemoryLog')
            self._logger = DoorPiMemoryLog()

        self._prepared = True
        return self

    def start(self, start_as_daemon=True):
        try:
            logger.debug('start')
            self._start_as_daemon = start_as_daemon

            # load now the libs, because now DoorPi can receive the module_register
            from resources.config import ConfigHandler
            from resources.event_handler import EventHandler
            from resources.interface_handler import InterfaceHandler

            self._core_documentation = ConfigHandler.get_module_documentation_by_module_name(__name__)

            try:
                self._config_handler = ConfigHandler()
                self._event_handler = EventHandler()
                self._interface_handler = InterfaceHandler()

                for module in [self._config_handler, self._event_handler, self._interface_handler]:
                    module.start()

            except Exception as exp:
                logger.exception("failed to start DoorPi with error %s" % exp)
                raise CorruptConfigFileException(exp)

            self.events.register_events(__name__)

            event_arguments = {'start_as_daemon': 'daemon' if start_as_daemon else 'application'}
            self.events.fire_event(__name__, 'BeforeStartup', kwargs=event_arguments)
            self.events.fire_event_synchron(__name__, 'OnStartup', kwargs=event_arguments)
            self.events.fire_event(__name__, 'AfterStartup', kwargs=event_arguments)

            while self._event_handler.heart_beat():
                pass
            return self
        except Exception as exp:
            logger.exception(exp)
            return False

    def stop(self):
        if not self.events:
            return False

        logger.debug('stop')
        logger.debug("Threads before starting shutdown: %s", self.events.threads)

        self.events.fire_event(__name__, 'BeforeShutdown')
        self.events.fire_event_synchron(__name__, 'OnShutdown')
        self.events.fire_event(__name__, 'AfterShutdown')

        timeout = self.CONST.DOORPI_SHUTDOWN_TIMEOUT
        waiting_between_checks = self.CONST.DOORPI_SHUTDOWN_TIMEOUT_CHECK_INTERVAL

        time.sleep(waiting_between_checks)
        while timeout > 0 and not self.modules_destroyed:
            # while not self.event_handler.idle and timeout > 0 and len(self.event_handler.sources) > 1:
            logger.info('wait %s seconds for threads: %s', timeout, self.events.threads[1:])
            time.sleep(waiting_between_checks)
            timeout -= waiting_between_checks

        if timeout <= 0:
            logger.warning("waiting for threads to time out - there are still threads: %s", self.events.threads[1:])

        logger.info('======== DoorPi successfully shutdown ========')
        if self.logger:
            self.logger.close()
        return self

    def restart_module(self, module_name):
        if module_name not in self._modules: return False
        if self._modules[module_name]['stop_function']:
            try:
                self._modules[module_name]['stop_function']()
            except Exception as exp:
                logger.exception('failed to stop module %s with error %s', module_name, exp)

    def unregister_module(self, module_name, execute_stop_function=False):
        if module_name not in self._modules: return False
        if execute_stop_function and self._modules[module_name]['stop_function']:
            try:
                self._modules[module_name]['stop_function']
            except Exception as exp:
                logger.exception('failed to stop module')
        del self._modules[module_name]
        return True

    def register_module(self, module_name, start_function=None, stop_function=None, return_new_logger=False):
        if module_name in self._modules:
            logger.info("update module %s", module_name)
        else:
            logger.info("register module %s", module_name)

        logger.debug("- with start_function:    %s", start_function)
        logger.debug("- with stop_function:     %s", stop_function)
        logger.debug("- with return_new_logger: %s", return_new_logger)

        self._modules[module_name] = dict(
            timestamp=time.time(),
            start_function=start_function,
            stop_function=stop_function
        )
        if not return_new_logger:
            return True
        else:
            return init_own_logger(module_name)

    run = start
    destroy = stop
    # __del__ = stop
