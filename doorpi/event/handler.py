import collections
import logging
import random
import string
import threading
import time

import doorpi
import doorpi.actions

from .log import EventLog


LOGGER = logging.getLogger(__name__)


def generate_id(size=6, chars=string.ascii_uppercase + string.digits):
    """Generates a random event ID."""
    return "".join(random.choice(chars) for _ in range(size))


class EventHandler:
    """The event handler and action dispatcher."""

    def __init__(self):
        conf = doorpi.DoorPi().config
        db_path = conf.get_string_parsed("DoorPi", "eventlog", "!BASEPATH!/conf/eventlog.db")
        self.log = EventLog(db_path)

        self.actions = collections.defaultdict(list)
        self.events = collections.defaultdict(set)
        self.extra_info = {}
        self.sources = []
        self.__active = True

        # register eventbased actions from configfile
        section = "EVENT_"
        for event_section in conf.get_sections(section):
            event = event_section[len(section):]
            LOGGER.info("Registering configured actions for %s", event)
            for key in sorted(conf.get_keys(event_section)):
                action = conf.get_string(event_section, key)
                LOGGER.debug("Registering action %s", repr(action))
                self.register_action(event, action)

        # register configured DTMF actions
        LOGGER.info("Registering DTMF actions")
        section = "DTMF"
        for key in conf.get_keys(section):
            action = conf.get_string(section, key)
            LOGGER.debug("Registering action %s for DTMF %s", action, key)
            self.register_action(f"OnDTMF_{key}", action)

    def destroy(self):
        """Waits for currently running actions, writes the log and destroys the handler."""
        self.__active = False
        self.log.destroy()

    @property
    def event_history(self):
        return self.log.get_event_log()

    @property
    def threads(self):
        """Lists event threads managed by the handler."""
        return [t for t in threading.enumerate() if t.name.startswith("DoorPi Event")]

    @property
    def idle(self):
        """Returns whether the handler is currently idle."""
        return not self.threads

    def get_events_by_source(self, source):
        """Groups all known events by the sources that can fire them."""
        return [ev for ev in self.events if source in self.events[ev]]

    def register_source(self, source):
        """Registers a new event source."""
        if source not in self.sources:
            self.sources.append(source)
            LOGGER.debug("Added event source %s", source)

    def register_event(self, event, source):
        """Registers an event to be fired from the named event source."""
        suppress_logs = _suppress_logs(event)
        if not suppress_logs: LOGGER.debug("Registering event %s with source %s", event, source)
        self.register_source(source)

        if source not in self.events[event]:
            self.events[event] |= {source}
            if not suppress_logs: LOGGER.debug("Registered source %s for event %s", source, event)
        else:
            LOGGER.warning("Multiple registrations for event %s from source %s", event, source)

    def fire_event(self, event, source, *, extra=None):
        """Asynchronously fires an event."""
        if not self.__active: return
        threading.Thread(
            target=self.fire_event_sync,
            args=(event, source),
            kwargs={"extra": extra},
            name=f"DoorPi Event {event} from {source}"
        ).start()

    def fire_event_sync(self, event, source, *, extra=None):
        """Synchronously fires an event."""
        if not self.__active: return

        suppress_logs = _suppress_logs(event)

        if source not in self.sources:
            LOGGER.warning("Unknown event source %s, skipping %s", source, event)
            return
        if event not in self.events:
            LOGGER.warning("Unknown event %s (from source %s), skipping", event, source)
            return
        if source not in self.events[event]:
            LOGGER.warning("Source %s not registered for %s, skipping", source, event)
            return

        if event not in self.actions:
            if not suppress_logs: LOGGER.debug("No actions registered for %s, skipping", event)
            return

        event_id = generate_id()
        start_time = time.time()

        if not suppress_logs:
            self.log.log_event(event_id, source, event, start_time, extra)

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
            LOGGER.debug("[%s] Executing %d action(s) for %s",
                         event_id, len(self.actions[event]), event)

        oneshot_actions = []
        for action in self.actions[event]:
            try:
                if not suppress_logs: LOGGER.debug("[%s] Executing %s", event_id, action)
                action(event_id, extra)
                if not suppress_logs: self.log.log_action(event_id, str(action), start_time)
            except Exception:
                try:
                    LOGGER.exception("[%s] Error executing action \"%s\" for event %s",
                                     event_id, action, event)
                except Exception:  # pylint: disable=broad-except
                    LOGGER.exception("[%s] Error executing an action")

            if "oneshot" in action.__dict__ and action.oneshot:
                oneshot_actions.append(action)

        for action in oneshot_actions:
            self.actions[event].remove(action)

        if not suppress_logs:
            LOGGER.debug("[%s] Finished firing event %s", event_id, event)

        self.extra_info[event]["last_finished"] = time.time()
        self.extra_info[event]["last_duration"] = time.time() - start_time

    def _unregister_event(self, event, source):
        suppress_logs = _suppress_logs(event)
        if not suppress_logs: LOGGER.debug("Unregistering event %s from source %s", event, source)

        if event not in self.events:
            LOGGER.error("Attempt to unregister unknown event %s", event)
            return False

        if source not in self.events[event]:
            LOGGER.error("Attempt to unregister unknown source %s from event %s", source, event)
            return False

        self.events[event] -= {source}
        if not self.events[event]:
            del self.events[event]

        return True

    def unregister_event(self, event, source):
        """Unregisters an event from a source."""
        if self._unregister_event(event, source):
            self.unregister_source(source, force=None)

    def unregister_source(self, source, *, force=False):
        """Unregisters an event source.

        Args:
            force: If True, unregisters a source even when it still has events associated.
        """
        LOGGER.debug("Removing source %s%s", source, " with force" if force else "")

        events = self.get_events_by_source(source)
        if events:
            if force is False:
                LOGGER.error("Attempt to unregister source %s, which is used for %d events: %s",
                             source, len(events), ", ".join(events))
            if not force:
                return

            for ev in events:
                self._unregister_event(ev, source)

        if source in self.sources:
            self.sources.remove(source)

    def register_action(self, event, action, *, oneshot=False):
        """Registers an action to execute when the named event fires.

        Args:
            oneshot: Only execute the action once and remove it afterwards.
        """
        if isinstance(action, str):
            action = doorpi.actions.from_string(action)
        elif not callable(action):
            raise ValueError("action must be a str or callable")

        if event not in self.actions:
            self.actions[event] = []
        self.actions[event].append(action)

        LOGGER.trace("Registered action %s for event %s", action, event)

    __call__ = fire_event


def _suppress_logs(event_name):
    return "OnTime" in event_name
