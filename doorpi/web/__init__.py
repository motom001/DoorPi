import logging
import os
import socket
import threading
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from urllib import request

import doorpi
from doorpi.actions import CallbackAction
from .sessions import SessionHandler
from .requests import DoorPiWebRequestHandler


LOGGER = logging.getLogger(__name__)
DOORPIWEB_SECTION = "DoorPiWeb"
CONF_AREA = "AREA_{area}"


def load():
    ip = doorpi.INSTANCE.config["web.ip"]
    port = doorpi.INSTANCE.config["web.port"]

    doorpiweb_object = None

    LOGGER.info("Starting WebService")
    try:
        server_address = (ip, port)
        doorpiweb_object = DoorPiWeb(server_address, DoorPiWebRequestHandler)
        doorpiweb_object.start()
    except Exception:  # pylint: disable=broad-except
        LOGGER.exception("Failed starting webserver")

    return doorpiweb_object


def check_config(config):
    return {"infos": [], "warnings": [], "errors": []}


class DoorPiWeb(ThreadingMixIn, HTTPServer):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.keep_running = True

        self.www = None
        self.indexfile = None
        self.base_url = None
        self.area_public_name = None

        self._thread = None

    @property
    def config_status(self):
        return check_config(self.config)

    @property
    def own_url(self):
        if self.server_port == 80:
            return f"http://{self.server_name}/"
        return f"http://{self.server_name}:{self.server_port}/"

    def inform_own_url(self):
        LOGGER.info("DoorPiWeb URL is %s", self.own_url)

    @property
    def sessions(self):
        if not self._session_handler and self.keep_running:
            LOGGER.debug("no session handler - creating it now")
            self._session_handler = SessionHandler()
        return self._session_handler
    _session_handler = None

    @property
    def config(self):
        return doorpi.INSTANCE.config

    def start(self):
        LOGGER.info("Starting WebServer on %s", self.own_url)
        eh = doorpi.INSTANCE.event_handler
        eh.register_event("OnWebServerStart", __name__)
        eh.register_event("OnWebServerStop", __name__)

        conf = doorpi.INSTANCE.config
        self.www = conf["web.root"]
        self.indexfile = "index.html"
        self.area_public_name = "public"
        LOGGER.info("Serving files from %s", self.www)

        eh.register_action("OnShutdown", CallbackAction(self.init_shutdown))
        self._thread = threading.Thread(
            target=self.serve_forever, name="Webserver Thread")
        eh.register_action("OnStartup", CallbackAction(self._thread.start))
        eh.fire_event_sync("OnWebServerStart", __name__)

        DoorPiWebRequestHandler.prepare()
        LOGGER.info("WebServer started")
        return self

    def fake_request(self):
        try:
            request.urlopen(self.own_url, timeout=0)
        except OSError:
            pass

    def init_shutdown(self):
        doorpi.INSTANCE.event_handler.fire_event_sync(
            "OnWebServerStop", __name__)
        self.shutdown()
        if self.sessions: self.sessions.destroy()
        DoorPiWebRequestHandler.destroy()
        self.fake_request()
        self._thread.join()
        doorpi.INSTANCE.event_handler.unregister_source(__name__, force=True)

    def server_bind(self):
        listen_fds = int(os.environ.get("LISTEN_FDS", 0))
        if listen_fds > 0:
            LOGGER.trace("Passed in fds: {}".format(listen_fds))
            fd = 3  # defined as SD_LISTEN_FDS_START in <systemd/sd-daemon.h>
            self.socket = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
            # fake out some info that isn't readily available in this mode
            self.server_name = "<your-raspberry-ip>:port"
            self.server_port = 80
        else:
            super().server_bind()

    def server_activate(self):
        listen_fds = int(os.environ.get("LISTEN_FDS", 0))
        if listen_fds == 0:
            super().server_activate()
