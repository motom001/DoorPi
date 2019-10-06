import collections
import logging
import os
import random
import string
import threading
import time

import doorpi
import doorpi.actions

from .log import EventLog


logger = logging.getLogger(__name__)


def generate_id(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


class EventHandler:

    def __init__(self):
        conf = doorpi.DoorPi().config
        db_path = conf.get_string_parsed('DoorPi', 'eventlog', '!BASEPATH!/conf/eventlog.db')
        self.db = EventLog(db_path)

        self.actions = {}
        self.events = {}
        self.extra_info = {}
        self.sources = []
        self.__active = True

        # register eventbased actions from configfile
        section = "EVENT_"
        for event_section in conf.get_sections(section):
            event = event_section[len(section):]
            logger.info("Registering configured actions for %s", event)
            for key in sorted(conf.get_keys(event_section)):
                action = conf.get_string(event_section, key)
                logger.debug("Registering action %s", repr(action))
                self.register_action(event, action)

        # register configured DTMF actions
        logger.info("Registering DTMF actions")
        section = "DTMF"
        for key in conf.get_keys(section):
            action = conf.get_string(section, key)
            logger.debug("Registering action %s for DTMF %s", action, key)
            self.register_action(f"OnDTMF_{key}", action)

    def destroy(self):
        self.__active = False
        self.db.destroy()

    @property
    def event_history(self): return self.db.get_event_log()

    @property
    def threads(self):
        return [t for t in threading.enumerate() if t.name.startswith("DoorPi Event")]

    @property
    def idle(self):
        return len(self.threads) == 0

    def get_events_by_source(self, source):
        return [ev for ev in self.events if source in self.events[ev]]

    def register_source(self, source):
        if source not in self.sources:
            self.sources.append(source)
            logger.debug("Added event source %s", source)

    def register_event(self, event, source):
        suppress_logs = _suppress_logs(event)
        if not suppress_logs: logger.debug("Registering event %s with source %s", event, source)
        self.register_source(source)

        if event not in self.events:
            self.events[event] = []
            if not suppress_logs: logger.debug("Registered event %s", event)

        if source not in self.events[event]:
            self.events[event].append(source)
            if not suppress_logs: logger.debug("Registered source %s for event %s", source, event)
        else:
            logger.warning("Multiple registrations for event %s from source %s", event, source)

    def fire_event(self, event, source, *, extra=None):
        if not self.__active: return
        threading.Thread(
            target=self.fire_event_sync,
            args=(event, source),
            kwargs={"extra": extra},
            name=f"DoorPi Event {event} from {source}"
        ).start()

    def fire_event_sync(self, event, source, *, extra=None):
        if not self.__active: return

        suppress_logs = _suppress_logs(event)

        if source not in self.sources:
            logger.warning("Unknown event source %s, skipping %s", source, event)
            return
        if event not in self.events:
            logger.warning("Unknown event %s (from source %s), skipping", event, source)
            return
        if source not in self.events[event]:
            logger.warning("Source %s not registered for %s, skipping", source, event)
            return

        if event not in self.actions:
            if not suppress_logs: logger.debug("No actions registered for %s, skipping", event)
            return

        event_id = generate_id()
        start_time = time.time()

        if not suppress_logs:
            self.db.log_event(event_id, source, event, start_time, extra)

        if extra is None: extra = {}
        extra.update({
            "last_fired": str(start_time),
            "source": source,
            "event_id": event_id
        })

        # copy over info from last event run
        last_info = self.extra_info.get(event, {})
        for key in ["last_finished", "last_duration"]:
            extra[key] = last_info.get(key, None)
        self.extra_info[event] = extra

        if not suppress_logs:
            logger.debug("[%s] Executing %d action(s) for %s",
                         event_id, len(self.actions[event]), event)

        oneshot_actions = []
        for action in self.actions[event]:
            try:
                if not suppress_logs: logger.debug("[%s] Executing %s", event_id, action)
                action(event_id, extra)
                if not suppress_logs: self.db.log_action(event_id, str(action), start_time)
            except Exception:
                logger.exception("[%s] Error executing action '%s' for event %s",
                                 event_id, repr(action), event)

            if "oneshot" in action.__dict__ and action.oneshot:
                oneshot_actions.append(action)

        for action in oneshot_actions:
            self.actions[event].remove(action)

        if not suppress_logs:
            logger.debug("[%s] Finished firing event %s", event_id, event)

        self.extra_info[event]['last_finished'] = time.time()
        self.extra_info[event]['last_duration'] = time.time() - start_time

    def _unregister_event(self, event, source):
        suppress_logs = _suppress_logs(event)
        if not suppress_logs: logger.debug("Unregistering event %s from source %s", event, source)

        if event not in self.events:
            logger.error("Attempt to unregister unknown event %s", event)
            return False

        if source not in self.events[event]:
            logger.error("Attempt to unregister unknown source %s from event %s", source, event)
            return False

        self.events[event].remove(source)
        if len(self.events[event]) == 0:
            del self.events[event]

        return True

    def unregister_event(self, event, source):
        if self._unregister_event(event, source):
            self.unregister_source(source, force=None)

    def unregister_source(self, source, *, force=False):
        logger.debug("Removing source %s%s", source, " with force" if force else "")

        events = self.get_events_by_source(source)
        if len(events) > 0:
            if force is False:
                logger.error("Attempt to unregister source %s, which is used for %d events: %s",
                             source, len(events), ", ".join(events))
            if not force:
                return

            for ev in events: self._unregister_event(ev, source)

        if source in self.sources:
            self.sources.remove(source)

    def register_action(self, event, action, *, oneshot=False):
        if isinstance(action, str):
            action = doorpi.actions.from_string(action)
        elif not isinstance(action, doorpi.actions.Action):
            raise ValueError("action must be a str or doorpi.actions.Action")

        if event not in self.actions:
            self.actions[event] = []
        self.actions[event].append(action)

        logger.trace("Registered action %s for event %s", action, event)

    __del__ = destroy
    __call__ = fire_event


def _suppress_logs(event_name):
    return "OnTime" in event_name
