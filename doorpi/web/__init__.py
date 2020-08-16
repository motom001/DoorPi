"""The DoorPiWeb server"""
import logging
import os
import socket
import threading
import http.server

import doorpi
from doorpi.actions import CallbackAction

LOGGER = logging.getLogger(__name__)

try:
    from . import requests, sessions
except ImportError as err:
    LOGGER.error("DoorPiWeb requirements are not met: %s", err)
    def load():
        pass
else:
    def load():
        """Load the webserver"""
        try:
            doorpiweb_object = DoorPiWeb()
            doorpiweb_object.start()
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("Failed starting webserver")

        return doorpiweb_object


class DoorPiWeb(http.server.ThreadingHTTPServer):
    """The DoorPiWeb server"""
    def __init__(self):
        self.config = doorpi.INSTANCE.config.view("web")

        self.sessions = None
        self.www = self.config["root"]

        self._thread = None

        address = (self.config["ip"], self.config["port"])
        super().__init__(address, requests.DoorPiWebRequestHandler)

        eh = doorpi.INSTANCE.event_handler
        eh.register_event("OnWebServerStart", __name__)
        eh.register_event("OnWebServerStop", __name__)

    def start(self):
        """Start the web server"""
        LOGGER.info(
            "Starting web server on http://%s:%d",
            self.server_name, self.server_port)
        self.sessions = sessions.SessionHandler()

        LOGGER.info("Serving files from %s", self.www)

        eh = doorpi.INSTANCE.event_handler
        eh.register_action("OnShutdown", CallbackAction(self.shutdown))
        self._thread = threading.Thread(
            target=self.serve_forever, name="Webserver Thread")
        eh.register_action("OnStartup", CallbackAction(self._thread.start))
        eh.fire_event_sync("OnWebServerStart", __name__)

        requests.DoorPiWebRequestHandler.prepare()
        LOGGER.info("WebServer started")
        return self

    def shutdown(self):
        doorpi.INSTANCE.event_handler.fire_event_sync(
            "OnWebServerStop", __name__)
        super().shutdown()
        if self.sessions:
            self.sessions.destroy()
        requests.DoorPiWebRequestHandler.destroy()
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
