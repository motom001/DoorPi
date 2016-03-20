# -*- coding: utf-8 -*-
from resources.logging import DoorPiMemoryLog, init_own_logger
import time
import os
import string
import random
import main

logger = init_own_logger(__name__)


class CorruptConfigFileException(Exception):
    pass


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
        return vars(self._arguments)

    @property
    def CONST(self):
        return main.CONST

    @property
    def libraries(self):
        doc = self.config.get_module_documentation_by_module_name(__name__)
        if doc is None:
            return {'libraries': []}
        else:
            return doc['libraries']

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
        logger.debug(_('restart'))
        self.stop()
        self.__init__()
        self.start()

    def prepare(self, arguments):
        logger = init_own_logger(__name__)

        if arguments:
            self._arguments = arguments

        if not self._logger:
            logger.debug(_('set new logger DoorPiMemoryLog'))
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

            try:
                self._config_handler = ConfigHandler()
                self._event_handler = EventHandler()
                self._interface_handler = InterfaceHandler()
                print self.config.dump_object(
                    self.config.get_module_documentation_by_module_name("resources.interface_handler")
                )

                for module in [self._config_handler, self._event_handler, self._interface_handler]:
                    module.start()

            except Exception as exp:
                logger.exception(_("failed to start DoorPi with error %s") % exp)
                raise CorruptConfigFileException(exp)

            self.events.register_events(__name__)

            self.events.fire_event(__name__, 'BeforeStartup', kwargs=self.arguments)
            self.events.fire_event_synchron(__name__, 'OnStartup', kwargs=self.arguments)
            self.events.fire_event(__name__, 'AfterStartup', kwargs=self.arguments)

            if self._arguments.create_parsed_docs:
                return self.create_parsed_docs()

            test_mode_counter = 0
            while self._event_handler.heart_beat():
                if self._arguments.test_mode and test_mode_counter > 1000:
                    logger.info(_("stop test_mode now"))
                    return self
                elif self._arguments.test_mode:
                    test_mode_counter += 1
            return self
        except Exception as exp:
            logger.exception(exp)
            return False

    def stop(self):
        if not self.events:
            return False

        logger.debug(_('stop'))
        logger.debug(_("Threads before starting shutdown: %s"), self.events.threads)

        self.events.fire_event(__name__, 'BeforeShutdown', kwargs=self.arguments)
        self.events.fire_event_synchron(__name__, 'OnShutdown', kwargs=self.arguments)
        self.events.fire_event(__name__, 'AfterShutdown', kwargs=self.arguments)

        timeout = self.CONST.DOORPI_SHUTDOWN_TIMEOUT
        waiting_between_checks = self.CONST.DOORPI_SHUTDOWN_TIMEOUT_CHECK_INTERVAL

        time.sleep(waiting_between_checks)
        while timeout > 0 and not self.modules_destroyed:
            # while not self.event_handler.idle and timeout > 0 and len(self.event_handler.sources) > 1:
            logger.info(_('wait %s seconds for threads: %s'), timeout, self.events.threads[1:])
            time.sleep(waiting_between_checks)
            timeout -= waiting_between_checks

        if timeout <= 0:
            logger.warning(_("waiting for threads to time out - there are still threads: %s"), self.events.threads[1:])

        logger.info(_('======== DoorPi successfully shutdown ========'))
        if self.logger:
            self.logger.close()
        return self

    def create_parsed_docs(self):
        logger.info(_("create_parsed_docs start"))
        return self

    def restart_module(self, module_name):
        if module_name not in self._modules: return False
        if self._modules[module_name]['stop_function']:
            try:
                self._modules[module_name]['stop_function']()
            except Exception as exp:
                logger.exception(_('failed to stop module %s with error %s'), module_name, exp)

    def unregister_module(self, module_name, execute_stop_function=False):
        if module_name not in self._modules: return False
        if execute_stop_function and self._modules[module_name]['stop_function']:
            try:
                self._modules[module_name]['stop_function']
            except Exception as exp:
                logger.exception('failed to stop module: %s', exp)
        del self._modules[module_name]
        return True

    def register_module(self, module_name, start_function=None, stop_function=None, return_new_logger=False):
        if module_name in self._modules:
            logger.info(_("update module %s"), module_name)
        else:
            logger.info(_("register module %s"), module_name)

        logger.debug(_("- with start_function:    %s"), start_function)
        logger.debug(_("- with stop_function:     %s"), stop_function)
        logger.debug(_("- with return_new_logger: %s"), return_new_logger)

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
