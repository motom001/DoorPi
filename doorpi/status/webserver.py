import logging
import os
import socket
import threading
from http.server import HTTPServer
from socketserver import ThreadingMixIn
from urllib import request

import doorpi
from doorpi.actions import CallbackAction
from doorpi.status.webserver_lib.session_handler import SessionHandler
from doorpi.status.webserver_lib.request_handler import DoorPiWebRequestHandler


LOGGER = logging.getLogger(__name__)
DOORPIWEB_SECTION = "DoorPiWeb"
CONF_AREA = "AREA_{area}"


def load_webserver():
    ip = doorpi.DoorPi().config.get_string(DOORPIWEB_SECTION, "ip", "0.0.0.0")
    port = doorpi.DoorPi().config.get_int(DOORPIWEB_SECTION, "port", 50371)

    doorpiweb_object = None

    LOGGER.info("Starting WebService")
    try:
        server_address = (ip, port)
        doorpiweb_object = DoorPiWeb(server_address, DoorPiWebRequestHandler)
        doorpiweb_object.start()
    except Exception:
        LOGGER.exception("Failed starting webserver")

    return doorpiweb_object


def check_config(config):
    errors = []
    warnings = []
    infos = []

    groups_with_write_permissions = config.get_keys("WritePermission")
    groups_with_read_permissions = config.get_keys("ReadPermission")
    groups = config.get_keys("Group")
    users = config.get_keys("User")

    if len(groups) == 0:
        errors.append("no groups in configfile!")

    if len(groups_with_write_permissions) == 0:
        errors.append("no WritePermission found")

    for group in groups_with_write_permissions:
        if group not in groups:
            warnings.append("group %s doesn't exist but is assigned to WritePermission" % group)

    if len(groups_with_read_permissions) == 0:
        warnings.append("no ReadPermission found")

    for group in groups_with_read_permissions:
        if group not in groups:
            warnings.append("group %s doesn't exist but is assigned to ReadPermission" % group)

    for group in groups:
        users_in_group = config.get_list("Group", group)
        for user_in_group in users_in_group:
            if user_in_group not in users:
                warnings.append("user %s is assigned to group %s but doesn't exist as user"
                                % (user_in_group, group))

    config_section = config.get_sections()

    for group in groups_with_write_permissions:
        for perm in ["WritePermission", "ReadPermission"]:
            modules = config.get_list(perm, group)
            for module in modules:
                if CONF_AREA.format(area=module) not in config_section:
                    warnings.append("module %s doesn't exist but is assigned to group %s in %s"
                                    % (module, group, perm))

    for info in infos:
        LOGGER.info(info)
    for warning in warnings:
        LOGGER.error(warning)
    for error in errors:
        LOGGER.error(error)

    return {"infos": infos, "warnings": warnings, "errors": errors}


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
        return doorpi.DoorPi().config

    def start(self):
        LOGGER.info("Starting WebServer on %s", self.own_url)
        eh = doorpi.DoorPi().event_handler
        eh.register_event("OnWebServerStart", __name__)
        eh.register_event("OnWebServerStop", __name__)

        conf = doorpi.DoorPi().config
        self.www = os.path.realpath(conf.get_string_parsed(
            DOORPIWEB_SECTION, "www", "!BASEPATH!/../DoorPiWeb"))
        self.indexfile = conf.get_string_parsed(DOORPIWEB_SECTION, "indexfile", "index.html")
        self.area_public_name = conf.get_string_parsed(DOORPIWEB_SECTION, "public", "AREA_public")
        check_config(self.config)
        LOGGER.info("Serving files from %s", self.www)

        eh.register_action("OnShutdown", CallbackAction(self.init_shutdown))
        self._thread = threading.Thread(target=self.serve_forever, name="Webserver Thread")
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
        doorpi.DoorPi().event_handler.fire_event_sync("OnWebServerStop", __name__)
        self.shutdown()
        if self.sessions: self.sessions.destroy()
        DoorPiWebRequestHandler.destroy()
        self.fake_request()
        self._thread.join()
        doorpi.DoorPi().event_handler.unregister_source(__name__, force=True)

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
