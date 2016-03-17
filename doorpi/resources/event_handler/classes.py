#!/usr/bin/env python
# -*- coding: utf-8 -*-

from main import DOORPI
from time import sleep
from inspect import getargspec

logger = DOORPI.register_module(__name__, return_new_logger=True)


class MessageBaseClass(object):
    sender = ''
    event_name = ''
    parameters = dict()

    def fire(self):
        pass

    def get(self):
        return self.__dict__


class EventBaseClass:
    def __init__(self, event_name):
        self.name = event_name
        self.sources = []
        self.actions = []


class ActionBaseClass:
    @property
    def single_fire_action(self):
        return 'single_fire_action' in self._kwargs.keys() and self._kwargs['single_fire_action'] is True

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        if len(self._kwargs):
            return "[%s] %s with kwargs %s" % (
                self.id,
                self.action_name,
                self._kwargs
            )
        else:
            return "[%s] %s" % (
                self.id,
                self.action_name
            )

    def __init__(self, callback, id=None, **kwargs):
        self._id = id or DOORPI.generate_id(prefix='Action_')
        self._callback = callback
        self._kwargs = kwargs
        if len(self.__class__.__bases__) is 0:
            self.action_name = str(callback)
        else:
            self.action_name = self.__class__.__name__

    def run(self, **kwargs):
        kwargs.update(self._kwargs)
        arg_spec = getargspec(self._callback)
        if arg_spec.keywords is not None:
            return self._callback(kwargs)

        needed_arguments = {}
        for given_argument in kwargs.keys():
            if given_argument in arg_spec.args:
                needed_arguments[given_argument] = kwargs[given_argument]
        return self._callback(**needed_arguments)

    def to_string(self):
        return self.name

    __str__ = to_string


class EventHistoryHandler:
    def start(self, db_type, connection_string):
        connection_string = DOORPI.parse_string(connection_string)
        logger.info('open %s db for event history with connection string "%s"', db_type, connection_string)
        return self

    def stop(self):
        logger.info('stop event history handler')
        return self
