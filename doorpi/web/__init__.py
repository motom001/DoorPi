"""The DoorPiWeb server"""
from __future__ import annotations

import logging
import os
import pathlib
import socket
import threading
import http.server
from typing import Optional

import doorpi
from doorpi.actions import CallbackAction

LOGGER: doorpi.DoorPiLogger = logging.getLogger(__name__)  # type: ignore

try:
    from . import requests, sessions
except ImportError as err:
    LOGGER.error("DoorPiWeb requirements are not met: %s", err)
    def load() -> Optional[DoorPiWeb]:
        """Load the webserver"""
        return None
else:
    def load() -> Optional[DoorPiWeb]:
        """Load the webserver"""
        try:
            doorpiweb_object = DoorPiWeb()
            return doorpiweb_object
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("Failed to start webserver")
            return None


class DoorPiWeb(http.server.ThreadingHTTPServer):
    """The DoorPiWeb server"""
    def __init__(self) -> None:
        self.config = doorpi.INSTANCE.config.view("web")
        self.sessions = sessions.SessionHandler()
        self.www: pathlib.Path = self.config["root"]
        self._thread = threading.Thread(
            target=self.serve_forever, name="Webserver Thread")

        super().__init__(
            (self.config["ip"], self.config["port"]),
            requests.DoorPiWebRequestHandler)
        LOGGER.info(
            "Starting web server on http://%s:%d",
            self.server_name, self.server_port)
        LOGGER.info("Serving files from %s", self.www)

        requests.DoorPiWebRequestHandler.prepare()

        eh = doorpi.INSTANCE.event_handler
        eh.register_event("OnWebServerStart", __name__)
        eh.register_event("OnWebServerStop", __name__)
        eh.register_action("OnShutdown", CallbackAction(self.shutdown))
        eh.register_action("OnStartup", CallbackAction(self._thread.start))
        eh.fire_event_sync("OnWebServerStart", __name__)
        LOGGER.info("WebServer started")

    def shutdown(self) -> None:
        doorpi.INSTANCE.event_handler.fire_event_sync(
            "OnWebServerStop", __name__)
        super().shutdown()
        if self.sessions:
            self.sessions.destroy()
        requests.DoorPiWebRequestHandler.destroy()
        self._thread.join()
        doorpi.INSTANCE.event_handler.unregister_source(__name__, force=True)

    def server_bind(self) -> None:
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

    def server_activate(self) -> None:
        listen_fds = int(os.environ.get("LISTEN_FDS", 0))
        if listen_fds == 0:
            super().server_activate()
