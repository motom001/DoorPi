# -*- coding: utf-8 -*-

from main import DOORPI
import os

logger = DOORPI.register_module(__name__, return_new_logger=True)


class InterfaceStopAction(DOORPI.events.action_base_class):
    pass


class InterfaceBaseClass(object):
    _id = DOORPI.generate_id(prefix='Interface_')
    _conf = None
    _name = ''
    _channels = dict()

    _destroyed = False

    @property
    def id(self): return self._id

    @property
    def is_destroyed(self): return self._destroyed

    @property
    def fullname(self): return "[%s] %s (%s.%s)" % (self._id, self._name, self.module_name, self.class_name)

    @property
    def name(self): return self._name

    @property
    def module_name(self): return self.__class__.__module__

    @property
    def class_name(self): return self.__class__.__name__

    @property
    def channels(self): return self._channels.keys()

    @property
    def interface_info(self): return {
        'class_name': self.class_name,
        'module_name': self.module_name,
        'interface_name': self.name,
        'interface_id': self.id
    }

    def interface_name_variations(self, prefix='', postfix=''):
        return [
            "",
            "%s%s%s" % (prefix, self.name, postfix),
            "%s%s%s" % (prefix, self.module_name, postfix),
            "%s%s.%s%s" % (prefix, self.module_name, self.name, postfix)
        ]

    def __init__(self, name, config_path):
        self._name = name
        self._conf = config_path
        self._register_destroy_action()

    def start(self):
        logger.info('%s starting', self.fullname)

    def stop(self):
        logger.info('%s stopping', self.fullname)
        DOORPI.events.unregister_source(self._id)

    def _register_destroy_action(self, stop_function=None):
        if stop_function is None:
            stop_function = self.stop
        return DOORPI.events.register_action(InterfaceStopAction(stop_function), 'OnShutdown')
