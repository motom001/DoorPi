#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import threading
import time # used by: fire_event_synchron
from inspect import isfunction, ismethod # used by: register_action
import string, random # used by event_id

import sqlite3
import os

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

class EventLog(object):

    _db = False

    #doorpi.DoorPi().conf.get_string_parsed('DoorPi', 'eventlog', '!BASEPATH!/conf/eventlog.db')
    def __init__(self, file_name):

        if not file_name: return
        try:
            if not os.path.exists(os.path.dirname(file_name)):
                logger.info('Path %s does not exist - creating it now', os.path.dirname(file_name))
                os.makedirs(os.path.dirname(file_name))
            #https://docs.python.org/2/library/sqlite3.html#sqlite3.connect
            self._db = sqlite3.connect(
                database = file_name,
                timeout = 1,
                check_same_thread = False
            )

            self.execute_sql('''
                CREATE TABLE IF NOT EXISTS event_log (
                    event_id TEXT,
                    fired_by TEXT,
                    event_name TEXT,
                    start_time REAL,
                    additional_infos TEXT
                );'''
            )
            self.execute_sql('''
                CREATE TABLE IF NOT EXISTS action_log (
                    event_id TEXT,
                    action_name TEXT,
                    start_time REAL,
                    action_result TEXT
                );'''
            )
        except:
            logger.error('error to create event_db')

    def get_event_log_entries_count(self, filter = ''):
        logger.debug('request event logs count with filter %s', filter)
        try:
            return self.execute_sql('''
            SELECT COUNT(*)
            FROM event_log
            WHERE event_id LIKE '%{filter}%'
            OR fired_by LIKE '%{filter}%'
            OR event_name LIKE '%{filter}%'
            OR start_time LIKE '%{filter}%'
            '''.format(filter = filter)).fetchone()[0]
        except Exception as exp:
            logger.exception(exp)
            return -1

    def get_event_log_entries(self, max_count = 100, filter = ''):
        logger.debug('request last %s event logs with filter %s', max_count, filter)
        return_object = []
        sql_statement = '''
            SELECT
                event_id,
                fired_by,
                event_name,
                start_time,
                additional_infos
            FROM event_log
            WHERE event_id LIKE '%{filter}%'
            OR fired_by LIKE '%{filter}%'
            OR event_name LIKE '%{filter}%'
            OR start_time LIKE '%{filter}%'
            ORDER BY start_time DESC
            LIMIT {max_count}'''.format(max_count = max_count, filter = filter)

        for single_row in self.execute_sql(sql_statement):
            return_object.append({
                'event_id': single_row[0],
                'fired_by': single_row[1],
                'event_name': single_row[2],
                'start_time': single_row[3],
                'additional_infos': single_row[4]
            })
        return return_object

    def execute_sql(self, sql):
        if not self._db: return
        #logger.trace('fire sql: %s', sql)
        return self._db.execute(sql)

    def insert_event_log(self, event_id, fired_by, event_name, start_time, additional_infos):
        sql_statement = '''
        INSERT INTO event_log VALUES (
            "{event_id}","{fired_by}","{event_name}",{start_time},"{additional_infos}"
        );
        '''.format(
            event_id = event_id,
            fired_by = fired_by.replace('"', "'"),
            event_name = event_name.replace('"', "'"),
            start_time = start_time,
            additional_infos = str(additional_infos).replace('"', "'")
        )
        self.execute_sql(sql_statement)

    def insert_action_log(self, event_id, action_name, start_time, action_result):
        sql_statement = '''
        INSERT INTO action_log VALUES (
            "{event_id}","{action_name}",{start_time},"{action_result}"
        );
        '''.format(
            event_id = event_id,
            action_name = action_name.replace('"', "'"),
            start_time = start_time,
            action_result = str(action_result).replace('"', "'")
        )
        self.execute_sql(sql_statement)

    def update_event_log(self):
        pass

    def destroy(self):
        try: self._db.close()
        except: pass

    __del__ = destroy

class EventHandler:

    __Sources = [] # Auflistung Sources
    __Events = {} # Zuordnung Event zu Sources (1 : n)
    __Actions = {} # Zuordnung Event zu Actions (1: n)

    __additional_informations = {}

    @property
    def event_history(self): return self.db.get_event_log_entries()

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

    def __init__(self):
        db_path = doorpi.DoorPi().config.get_string_parsed('DoorPi', 'eventlog', '!BASEPATH!/conf/eventlog.db')
        self.db = EventLog(db_path)

    __destroy = False

    def destroy(self, force_destroy = False):
        self.__destroy = True
        self.db.destroy()

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
            if not silent: logger.trace("added event_name %s and registered source %s", event_name, event_source)
        elif event_source not in self.__Events[event_name]:
            self.__Events[event_name].append(event_source)
            if not silent: logger.trace("added event_source %s to existing event %s", event_source, event_name)
        else:
            if not silent: logger.trace("nothing to do - event %s from source %s is already known", event_name, event_source)

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
        start_time = time.time()
        if not silent: self.db.insert_event_log(event_fire_id, event_source, event_name, start_time, kwargs)

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
                result = action.run(silent)
                if not silent: self.db.insert_action_log(event_fire_id, action.name, start_time, result)
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
        try:
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
        except Exception as exp:
            logger.error('failed to unregister event %s with error message %s', event_name, exp)
            return False

    def unregister_source(self, event_source, force_unregister = False):
        try:
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
        except Exception as exp:
            logger.exception('failed to unregister source %s with error message %s', event_source, exp)
            return False

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

        return action_object

    __call__ = fire_event_asynchron
