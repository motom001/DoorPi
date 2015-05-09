#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import threading
import time # used by: fire_event_synchron
from inspect import isfunction, ismethod # used by: register_action
import string, random # used by event_id

from base import SingleAction
import doorpi

class EnumWaitSignalsClass():
    WaitToFinish = True
    WaitToEnd = True
    sync = True
    syncron = True

    DontWaitToFinish = False
    DontWaitToEnd = False
    async = False
    asyncron = False
EnumWaitSignals = EnumWaitSignalsClass()

ONTIME = 'OnTime'

def id_generator(size = 6, chars = string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class EventHandler:

    __Sources = [] # Auflistung Sources
    __Events = {} # Zuordnung Event zu Sources (1 : n)
    __Actions = {} # Zuordnung Event zu Actions (1: n)

    __additional_informations = {}

    @property
    def sources(self): return self.__Sources
    @property
    def events(self): return self.__Events
    @property
    def events_by_source(self):
        events_by_source = {}
        for event in self.events:
            for source in self.events[event]:
                if source in events_by_source:
                    events_by_source[source].append(event)
                else:
                    events_by_source[source] = [event]
        return events_by_source
    @property
    def actions(self): return self.__Actions
    @property
    def threads(self): return threading.enumerate()
    @property
    def idle(self): return len(self.threads) - 1 is 0
    @property
    def additional_informations(self): return self.__additional_informations

    __destroy = False

    def destroy(self, force_destroy = False):
        self.__destroy = True

    def register_source(self, event_source):
        if event_source not in self.__Sources:
            self.__Sources.append(event_source)
            logger.debug("event_source %s was added", event_source)

    def register_event(self, event_name, event_source):
        silent = ONTIME in event_name
        if not silent: logger.trace("register Event %s from %s ", event_name, event_source)
        self.register_source(event_source)
        if event_name not in self.__Events:
            self.__Events[event_name] = [event_source]
            if not silent: logger.trace("added event_name %s an register source %s", event_name, event_source)
        elif event_source not in self.__Events[event_name]:
            self.__Events[event_name].append(event_source)
            if not silent: logger.trace("added event_source %s to existing event %s", event_source, event_name)
        else:
            if not silent: logger.trace("nothing to do - event %s from source %s is allready known", event_name, event_source)

    def fire_event(self, event_name, event_source, syncron = False, kwargs = None):
        if syncron is False: return self.fire_event_asynchron(event_name, event_source, kwargs)
        else: return self.fire_event_synchron(event_name, event_source, kwargs)

    def fire_event_asynchron(self, event_name, event_source, kwargs = None):
        silent = ONTIME in event_name
        if self.__destroy and not silent: return False
        if not silent: logger.trace("fire Event %s from %s asyncron", event_name, event_source)
        return threading.Thread(
            target = self.fire_event_synchron,
            args = (event_name, event_source, kwargs),
            name = "%s from %s" % (event_name, event_source)
        ).start()

    def fire_event_asynchron_daemon(self, event_name, event_source, kwargs = None):
        logger.trace("fire Event %s from %s asyncron and as daemons", event_name, event_source)
        t = threading.Thread(
            target = self.fire_event_synchron,
            args = (event_name, event_source, kwargs),
            name = "daemon %s from %s" % (event_name, event_source)
        )
        t.daemon = True
        t.start()

    def fire_event_synchron(self, event_name, event_source, kwargs = None):
        silent = ONTIME in event_name
        if self.__destroy and not silent: return False

        event_fire_id = id_generator()

        if event_source not in self.__Sources:
            logger.warning('source %s unknown - skip fire_event %s', event_source, event_name)
            return "source unknown"
        if event_name not in self.__Events:
            logger.warning('event %s unknown - skip fire_event %s from %s', event_name, event_name, event_source)
            return "event unknown"
        if event_source not in self.__Events[event_name]:
            logger.warning('source %s unknown for this event - skip fire_event %s from %s', event_name, event_name, event_source)
            return "source unknown for this event"
        if event_name not in self.__Actions:
            if not silent: logger.debug('no actions for event %s - skip fire_event %s from %s', event_name, event_name, event_source)
            return "no actions for this event"

        if kwargs is None: kwargs = {}
        start_time = time.time()
        kwargs.update({
            'last_fired': str(start_time),
            'last_fired_from': event_source,
            'event_fire_id': event_fire_id
        })

        self.__additional_informations[event_name] = kwargs
        if 'last_finished' not in self.__additional_informations[event_name]:
            self.__additional_informations[event_name]['last_finished'] = None

        if 'last_duration' not in self.__additional_informations[event_name]:
            self.__additional_informations[event_name]['last_duration'] = None

        if not silent: logger.debug("[%s] fire for event %s this actions %s ", event_fire_id, event_name, self.__Actions[event_name])
        for action in self.__Actions[event_name]:
            if not silent: logger.trace("[%s] try to fire action %s", event_fire_id, action)
            try:
                action.run(silent)
                if action.single_fire_action is True: del action
            except SystemExit as exp:
                logger.info('[%s] Detected SystemExit and shutdown DoorPi (Message: %s)', event_fire_id, exp)
                doorpi.DoorPi().destroy()
            except KeyboardInterrupt as exp:
                logger.info("[%s] Detected KeyboardInterrupt and shutdown DoorPi (Message: %s)", event_fire_id, exp)
                doorpi.DoorPi().destroy()
            except:
                logger.exception("[%s] error while fire action %s for event_name %s", event_fire_id, action, event_name)
        if not silent: logger.trace("[%s] finished fire_event for event_name %s", event_fire_id, event_name)
        self.__additional_informations[event_name]['last_finished'] = str(time.time())
        self.__additional_informations[event_name]['last_duration'] = str(time.time() - start_time)
        return True

    def unregister_event(self, event_name, event_source, delete_source_when_empty = True):
        logger.trace("unregister Event %s from %s ", event_name, event_source)
        if event_name not in self.__Events: return "event unknown"
        if event_source not in self.__Events[event_name]: return "source not know for this event"
        self.__Events[event_name].remove(event_source)
        if len(self.__Events[event_name]) is 0:
            del self.__Events[event_name]
            logger.debug("no more sources for event %s - remove event too", event_name)
        if delete_source_when_empty: self.unregister_source(event_source)
        logger.trace("event_source %s was removed for event %s", event_source, event_name)
        return True

    def unregister_source(self, event_source, force_unregister = False):
        logger.trace("unregister Eventsource %s and force_unregister is %s", event_source, force_unregister)
        if event_source not in self.__Sources: return "event_source %s unknown" % (event_source)
        for event_name in self.__Events.keys():
            if event_source in self.__Events[event_name] and force_unregister:
                self.unregister_event(event_name, event_source, False)
            elif event_source in self.__Events[event_name] and not force_unregister:
                return "couldn't unregister event_source %s because it is used for event %s" % (event_source, event_name)
        if event_source in self.__Sources:
            # sollte nicht nötig sein, da es entfernt wird, wenn das letzte Event dafür gelöscht wird
            self.__Sources.remove(event_source)
        logger.trace("event_source %s was removed", event_source)
        return True

    def register_action(self, event_name, action_object, *args, **kwargs):
        if ismethod(action_object) and callable(action_object):
            action_object = SingleAction(action_object, *args, **kwargs)
        elif isfunction(action_object) and callable(action_object):
            action_object = SingleAction(action_object, *args, **kwargs)
        elif not isinstance(action_object, SingleAction):
            action_object = SingleAction.from_string(action_object)

        if action_object is None:
            logger.error('action_object is None')
            return False

        if 'single_fire_action' in kwargs.keys() and kwargs['single_fire_action'] is True:
            action_object.single_fire_action = True
            del kwargs['single_fire_action']

        if event_name in self.__Actions:
            self.__Actions[event_name].append(action_object)
            logger.trace("action %s was added to event %s", action_object, event_name)
        else:
            self.__Actions[event_name] = [action_object]
            logger.trace("action %s was added to new evententry %s", action_object, event_name)

    __call__ = fire_event_asynchron
