import collections
import itertools
import logging
import random
import string
import threading
import time
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
    Union,
)

import doorpi.actions
import doorpi.event

from . import log

LOGGER: doorpi.DoorPiLogger = logging.getLogger(__name__)  # type: ignore

ActionCallable = Callable[[str, Mapping[str, Any]], Any]
RegistrableAction = Union[str, "doorpi.actions.Action", ActionCallable]


def generate_id() -> str:
    """Generates a random event ID."""
    size = 6
    chars = "".join((string.ascii_uppercase, string.digits))
    return "".join(random.choice(chars) for _ in range(size))


class EventHandler:
    """The event handler and action dispatcher."""

    actions: Dict[str, List[ActionCallable]]
    events: Dict[str, Set[str]]
    extra_info: Dict[str, Any]
    sources: List[str]

    __active: bool

    def __init__(self) -> None:
        conf = doorpi.INSTANCE.config
        db_path = conf["eventlog"]
        self.log = log.EventLog(db_path)

        self.actions = collections.defaultdict(list)
        self.events = collections.defaultdict(set)
        self.extra_info = {"LastKey": "NotSetYet", "event": {}}
        self.sources = []
        self.__active = True

        # register eventbased actions from configfile
        for event, actions in conf.view("events").items():
            LOGGER.info("Registering configured actions for %s", event)
            for action in actions:
                LOGGER.debug("Registering action %s", repr(action))
                self.register_action(event, action)

        # register configured DTMF actions
        LOGGER.info("Registering DTMF actions")
        for seq, actions in conf.view("sipphone.dtmf").items():
            for action in actions:
                LOGGER.debug("Registering action %r for DTMF %r", action, seq)
                self.register_action(f"OnDTMF_{seq}", action)

    def destroy(self) -> None:
        """Shut down the event handler"""
        self.__active = False
        self.log.destroy()

    @property
    def event_history(self) -> Tuple[log.EventLogEntry, ...]:
        return self.log.get_event_log()

    @property
    def threads(self) -> List[threading.Thread]:
        """List event threads managed by the handler"""
        return [
            t
            for t in threading.enumerate()
            if t.name.startswith("DoorPi Event")
        ]

    @property
    def idle(self) -> bool:
        """Return whether the handler is currently idle"""
        return not self.threads

    def get_events_by_source(self, source: str) -> Set[str]:
        """Group all known events by the sources that can fire them"""
        return {ev for ev in self.events if source in self.events[ev]}

    def register_source(self, source: str) -> None:
        """Register a new event source"""
        if source not in self.sources:
            self.sources.append(source)
            LOGGER.debug("Added event source %s", source)

    def register_event(self, event: str, source: str) -> None:
        """Register an event to be fired from the named event source"""
        suppress_logs = _suppress_logs(event)
        if not suppress_logs:
            LOGGER.debug("Registering event %s with source %s", event, source)
        self.register_source(source)

        if source not in self.events[event]:
            self.events[event].add(source)
            if not suppress_logs:
                LOGGER.debug(
                    "Registered source %s for event %s", source, event
                )
        else:
            LOGGER.warning(
                "Multiple registrations for event %s from source %s",
                event,
                source,
            )

    def fire_event(
        self, event: str, source: str, *, extra: Dict[str, Any] = None
    ) -> None:
        """Fire an event asynchronously"""
        if not self.__active:
            return
        threading.Thread(
            target=self.fire_event_sync,
            args=(event, source),
            kwargs={"extra": extra},
            name=f"DoorPi Event {event} from {source}",
        ).start()

    def fire_event_sync(
        self, event: str, source: str, *, extra: Dict[str, Any] = None
    ) -> None:
        """Fire an event synchronously"""
        if not self.__active:
            return

        if extra is None:
            extra = {}
        suppress_logs = _suppress_logs(event)

        if source not in self.sources:
            LOGGER.warning(
                "Unknown event source %s, skipping %s", source, event
            )
            return
        if event not in self.events:
            LOGGER.warning(
                "Unknown event %s (from source %s), skipping", event, source
            )
            return
        if source not in self.events[event]:
            LOGGER.warning(
                "Source %s not registered for %s, skipping", source, event
            )
            return

        if event not in self.actions:
            if not suppress_logs:
                LOGGER.debug("No actions registered for %s, skipping", event)
            return

        event_id = generate_id()
        start_time = time.time()

        if not suppress_logs:
            self.log.log_event(event_id, source, event, start_time, extra)

        extra.update(
            {
                "last_fired": str(start_time),
                "source": source,
                "event_id": event_id,
            }
        )

        # copy over info from last event run
        last_info = self.extra_info.get(event, {})
        for key in ["last_finished", "last_duration"]:
            extra[key] = last_info.get(key, None)
        self.extra_info[event] = extra

        if not suppress_logs:
            LOGGER.debug(
                "[%s] Executing %d action(s) for %s",
                event_id,
                len(self.actions[event]),
                event,
            )

        oneshot_actions = []
        for action in self.actions[event]:
            try:
                if not suppress_logs:
                    LOGGER.debug("[%s] Executing %s", event_id, action)
                action(event_id, extra)
                if not suppress_logs:
                    self.log.log_action(event_id, str(action), start_time)
            except doorpi.event.AbortEventExecution:
                LOGGER.info("[%s] Aborting event execution early")
            except Exception:  # pylint: disable=broad-except
                try:
                    LOGGER.exception(
                        '[%s] Error executing action "%s" for event %s',
                        event_id,
                        action,
                        event,
                    )
                except Exception:  # pylint: disable=broad-except
                    LOGGER.exception("[%s] Error executing an action")

            if getattr(action, "oneshot", False):
                oneshot_actions.append(action)

        for action in oneshot_actions:
            self.actions[event].remove(action)

        if not suppress_logs:
            LOGGER.debug("[%s] Finished firing event %s", event_id, event)

        self.extra_info[event]["last_finished"] = time.time()
        self.extra_info[event]["last_duration"] = time.time() - start_time

    def _unregister_event(self, event: str, source: str) -> bool:
        suppress_logs = _suppress_logs(event)
        if not suppress_logs:
            LOGGER.debug(
                "Unregistering event %s from source %s", event, source
            )

        if event not in self.events:
            LOGGER.error("Attempt to unregister unknown event %s", event)
            return False

        if source not in self.events[event]:
            LOGGER.error(
                "Attempt to unregister unknown source %s from event %s",
                source,
                event,
            )
            return False

        self.events[event] -= {source}
        if not self.events[event]:
            del self.events[event]

        return True

    def unregister_event(self, event: str, source: str) -> None:
        """Unregister an event from a source"""
        if self._unregister_event(event, source):
            self.unregister_source(source, force=None)

    def unregister_source(
        self,
        source: str,
        *,
        force: Optional[bool] = False,
    ) -> None:
        """Unregister an event source

        Args:
            force: If True, unregisters a source even when it still has
                events associated.
        """
        LOGGER.debug(
            "Removing source %s%s", source, " with force" if force else ""
        )

        events = self.get_events_by_source(source)
        if events:
            if force is False:
                LOGGER.error(
                    "Attempt to unregister source %s,"
                    " which is used for %d events: %s",
                    source,
                    len(events),
                    ", ".join(events),
                )
            if not force:
                return

            for ev in events:
                self._unregister_event(ev, source)

        if source in self.sources:
            self.sources.remove(source)

    def register_action(
        self,
        event: str,
        action: RegistrableAction,
        *,
        oneshot: bool = False,
    ) -> None:
        """Register an action to execute when the ``event`` fires

        Args:
            oneshot: Only execute the action once and remove it afterwards
        """
        action_obj: Optional[ActionCallable]
        if isinstance(action, str):
            action_obj = doorpi.actions.from_string(action)
        elif callable(action):
            action_obj = action
        else:
            raise ValueError("action must be a str or callable")

        if action_obj is None:
            return

        self.actions.setdefault(event, []).append(action_obj)

        LOGGER.trace("Registered action %s for event %s", action, event)

    __call__ = fire_event


def _suppress_logs(event_name: str) -> bool:
    return "OnTime" in event_name
