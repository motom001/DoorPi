import argparse
import cgi
import datetime
import logging
import signal
import sys
import tempfile
import time
import traceback
from pathlib import Path

from . import metadata
from doorpi import keyboard, sipphone
from doorpi.actions import CallbackAction
from doorpi.conf.config_object import ConfigObject
from doorpi.event.handler import EventHandler
from doorpi.status.status_class import DoorPiStatus
from doorpi.status.systemd import DoorPiSD
from doorpi.status.webserver import load_webserver


logger = logging.getLogger(__name__)

DEADLY_SIGNALS_ABORT = 3


class DoorPiNotExistsException(Exception): pass


class Singleton(type):

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DoorPi(metaclass=Singleton):

    @property
    def extra_info(self):
        if self.event_handler is None: return {}
        else: return self.event_handler.extra_info

    @property
    def status(self): return DoorPiStatus(self)

    def get_status(self, modules="", value="", name=""):
        return DoorPiStatus(self, modules, value, name)

    @property
    def epilog(self): return metadata.epilog

    @property
    def name(self): return str(metadata.package)

    @property
    def name_and_version(self): return f"{metadata.package} - version: {metadata.version}"

    @property
    def base_path(self):
        if self._base_path is None:
            self._base_path = Path.home()
            logger.info("Auto-selected BasePath %s", self._base_path)
        return self._base_path

    def __init__(self, argv):
        self.config = None
        self.dpsd = None
        self.event_handler = None
        self.keyboard = None
        self.sipphone = None
        self.webserver = None

        self._base_path = None

        self.__argv = argv
        self.__deadlysignals = 0
        self.__prepared = False
        self.__shutdown = False

        self.__last_tick = time.time()

    def doorpi_shutdown(self, time_until_shutdown=0):
        if time_until_shutdown > 0: time.sleep(time_until_shutdown)
        self.__shutdown = True

    def signal_shutdown(self, signum, stackframe):
        self.__shutdown = True
        self.__deadlysignals += 1
        logger.info("Caught deadly signal %s (%d / %d)", signal.Signals(signum).name,
                    self.__deadlysignals, DEADLY_SIGNALS_ABORT)

        if self.__deadlysignals >= DEADLY_SIGNALS_ABORT:
            raise Exception("Force-exiting due to signal")

    def prepare(self):
        logger.debug("prepare")
        logger.debug("given arguments argv: %s", self.__argv)
        self.dpsd = DoorPiSD()

        # setup signal handlers for HUP, INT, TERM
        handler = self.signal_shutdown
        signal.signal(signal.SIGHUP, handler)
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

        self.config = ConfigObject(self.__argv.configfile)
        self._base_path = self.config.get_string("DoorPi", "base_path", self.base_path)
        self.event_handler = EventHandler()

        # register own events
        for ev in ["BeforeStartup", "OnStartup", "AfterStartup",
                   "BeforeShutdown", "OnShutdown", "AfterShutdown",
                   "OnTimeTick", "OnTimeRapidTick"]:
            self.event_handler.register_event(ev, __name__)

        # register base actions
        self.event_handler.register_action("OnTimeTick", f"time_tick:{self.__last_tick}")

        # register modules
        self.webserver = load_webserver()
        self.keyboard = keyboard.load()
        self.sipphone = sipphone.load()
        self.sipphone.start()

        self.__prepared = True
        return self

    def __del__(self):
        self.destroy()

    def destroy(self):
        logger.debug("Shutting down DoorPi")
        self.__shutdown = True
        self.dpsd.stopping()

        if not self.__prepared: return

        logger.debug("Threads before starting shutdown: %s", self.event_handler.threads)

        self.event_handler.fire_event_sync("BeforeShutdown", __name__)
        self.event_handler.fire_event_sync("OnShutdown", __name__)
        self.event_handler.fire_event_sync("AfterShutdown", __name__)

        timeout = 5
        waiting_between_checks = 0.5

        while timeout > 0 and not self.event_handler.idle:
            logger.debug("Waiting %s seconds for %d events to finish",
                         timeout, len(self.event_handler.threads))
            logger.trace("Still existing event threads: %s", self.event_handler.threads)
            logger.trace("Still existing event sources: %s", self.event_handler.sources)
            time.sleep(waiting_between_checks)
            timeout -= waiting_between_checks

        if len(self.event_handler.sources) > 1:
            logger.warning("Some event sources did not shut down properly: %s",
                           self.event_handler.sources[1:])

        logger.info("======== DoorPi completed shutting down ========")

    def run(self):
        logger.debug("run")
        if not self.__prepared: self.prepare()

        self.event_handler.fire_event_sync("BeforeStartup", __name__)
        self.event_handler.fire_event_sync("OnStartup", __name__)
        self.event_handler.fire_event_sync("AfterStartup", __name__)

        logger.info('DoorPi started successfully')
        logger.info('BasePath is %s', self.base_path)
        if self.webserver:
            self.webserver.inform_own_url()
        else:
            logger.info('no Webserver loaded')

        # setup watchdog ping and signal startup success
        self.event_handler.register_action("OnTimeSecondUnevenNumber",
                                           CallbackAction(self.dpsd.watchdog))
        self.dpsd.ready()

        tickrate = 0.05  # seconds between OnTimeRapidTick events
        tickrate_slow = 10  # rapid ticks between OnTimeTick events
        last = time.time()
        next_slowtick = 0

        while not self.__shutdown:
            self.event_handler.fire_event_sync("OnTimeRapidTick", __name__)
            next_slowtick -= 1

            if next_slowtick <= 0:
                self.__last_tick = time.time()
                self.event_handler.fire_event_sync("OnTimeTick", __name__)
                next_slowtick = tickrate_slow

            now = time.time()
            duration = now - last

            if duration > tickrate:
                skipped_ticks = int(duration / tickrate)
                logger.warning("Tick took too long (%.1fms > %.1fms), skipping %d tick(s)",
                               duration * 1000, tickrate * 1000, skipped_ticks)
                logger.warning("registered actions for OnTimeRapidTick: %s",
                               self.event_handler.actions["OnTimeRapidTick"])
                logger.warning("registered actions for OnTimeTick: %s",
                               self.event_handler.actions["OnTimeTick"])
                duration %= tickrate
                last += skipped_ticks * tickrate
                next_slowtick -= skipped_ticks

            last += tickrate
            time.sleep(last - now)
        return self

    def parse_string(self, input_string):
        parsed_string = datetime.datetime.now().strftime(str(input_string))

        if self.keyboard is None or self.keyboard.last_key is None:
            self.extra_info['LastKey'] = "NotSetYet"
        else:
            self.extra_info['LastKey'] = str(self.keyboard.last_key)

        infos_as_html = '<table>'
        for key, val in self.extra_info.items():
            key = cgi.escape(str(key))
            val = cgi.escape(str(val)).replace("\r\n", "\n").replace("\n", "<br>")
            infos_as_html += f"<tr><td><b>{key}</b></td><td><i>{val}</i></td></tr>"
        infos_as_html += '</table>'

        mapping_table = {
            'INFOS_PLAIN': str(self.extra_info),
            'INFOS': infos_as_html,
            'BASEPATH': str(self.base_path),
            'last_tick': str(self.__last_tick)
        }

        for key, val in metadata.__dict__.items():
            if isinstance(val, str):
                mapping_table[key.upper()] = val

        if self.config:
            mapping_table.update({
                "LAST_SNAPSHOT": self.config.get_string("DoorPi", "last_snapshot")
            })

        if self.keyboard:
            mapping_table.update(self.keyboard._enumerate_outputs())

        for key, val in mapping_table.items():
            parsed_string = parsed_string.replace(f"!{key}!", val)

        for key, val in self.extra_info.items():
            parsed_string = parsed_string.replace(f"!{key}!", str(val))

        return parsed_string


if __name__ == '__main__':
    raise Exception("use main.py to start DoorPi")
