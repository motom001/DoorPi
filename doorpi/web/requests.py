"""The DoorPiWeb request handler"""

import html
import http.server
import itertools
import json
import logging
import os
import pathlib
import re
import sys
import urllib.parse

import jinja2

import doorpi
from doorpi import metadata
from doorpi.actions import snapshot
from . import templates

LOGGER = logging.getLogger(__name__)

PARSABLE_FILE_EXTENSIONS = {".html"}
DOORPIWEB_SECTION = "DoorPiWeb"


class AuthenticationRequiredError(Exception):
    """Authentication is required to access this resource"""


class BadRequestError(Exception):
    """The received request was invalid"""


class DoorPiWebRequestHandler(http.server.BaseHTTPRequestHandler):
    """The DoorPiWeb request handler"""
    def log_error(self, format, *args):  # pylint: disable=redefined-builtin
        LOGGER.error(f"[%s] {format}", self.client_address[0], *args)

    def log_message(self, format, *args):  # pylint: disable=redefined-builtin
        LOGGER.debug(f"[%s] {format}", self.client_address[0], *args)

    @classmethod
    def prepare(cls):
        """Do necessary preparations to start working"""
        eh = doorpi.INSTANCE.event_handler
        eh.register_event("OnWebServerRequest", __name__)
        eh.register_event("OnWebServerRequestGet", __name__)
        eh.register_event("OnWebServerRequestPost", __name__)
        eh.register_event("OnWebServerVirtualResource", __name__)
        eh.register_event("OnWebServerRealResource", __name__)

        # for do_control
        eh.register_event("OnFireEvent", __name__)
        eh.register_event("OnConfigKeySet", __name__)
        eh.register_event("OnConfigKeyDelete", __name__)

        if sys.platform == "linux":
            try:
                cachedir = pathlib.Path(os.environ["XDG_CACHE_HOME"])
            except KeyError:
                cachedir = pathlib.Path.home() / ".cache"
        elif sys.platform == "win32":
            cachedir = pathlib.Path(os.environ["TEMP"])
        else:
            cachedir = pathlib.Path.home()
        cachedir /= metadata.distribution.metadata["Name"]
        cachedir /= "templatecache"
        cachedir.mkdir(parents=True, exist_ok=True)
        cls.environment = jinja2.Environment(
            bytecode_cache=jinja2.FileSystemBytecodeCache(cachedir),
            loader=templates.DoorPiWebTemplateLoader(),
            undefined=jinja2.StrictUndefined,
        )

    @classmethod
    def destroy(cls):
        """Shut the request handlers down"""
        doorpi.INSTANCE.event_handler.unregister_source(__name__, force=True)
        del cls.environment

    def do_GET(self):  # pylint: disable=invalid-name
        """Callback for incoming GET requests"""
        path = urllib.parse.urlparse(self.path)

        if path.path == "/":
            self.return_redirection("/dashboard/pages/index.html")
            return

        try:
            self.check_authentication(path)

            if path.query:
                params = urllib.parse.parse_qs(path.query, strict_parsing=True)
                for key, val in params.items():
                    params[key] = [urllib.parse.unquote_plus(v) for v in val]
            else:
                params = {}
            api_endpoint = self.API_ENDPOINTS.get(
                path.path.split("/")[1], "_resource")

            result, mime = getattr(self, api_endpoint)(path.path, params)
        except BadRequestError:
            self.return_message(http_code=400)
        except AuthenticationRequiredError:
            self.return_message(http_code=401)
        except FileNotFoundError:
            self.return_message(http_code=404)
        else:
            if isinstance(result, dict):
                result = json_encoder.encode(result)
            self.return_message(result, mime)

    @staticmethod
    def list_directory(path):
        """Serve a listing of the directory's contents"""
        dirs = []
        files = []
        for item in path.iterdir():
            if os.path.isfile(item):
                files.append(item)
            else:
                dirs.append(item)

        return_html = "".join(itertools.chain(
            ("<!DOCTYPE html><html lang=\"en\"><head></head>"
             "<body><a href=\"..\">..</a><br/>",),
            (f"<a href=\"./{dir_}\">{dir_}</a><br/>" for dir_ in dirs),
            (f"<a href=\"./{file}\">{file}</a><br/>" for file in files),
            ("</body></html>",),
        ))
        return (return_html, "text/html")

    def return_redirection(self, location):
        """Serve a document that redirects to ``location``"""
        message = (
            "<html><head>"
            "<meta http-equiv=\"refresh\" content=\"0;url={location}\">"
            "</head><body>"
            "<a href=\"{location}\">{location}</a>"
            "</body></html>"
        ).format(location=html.escape(location, True))
        self.return_message(message, "text/html", 307, ("Location", location))

    def canonicalize_filename(self, url):
        """Canonicalize and validate the requested filename"""
        if not isinstance(url, pathlib.Path):
            url = pathlib.Path(url)
        if url.is_absolute():
            url = url.relative_to(url.root)
        url = (self.server.www / url).resolve()

        if self.server.www in url.parents:
            return url

        snapshot_base = snapshot.SnapshotAction.get_base_path()
        if snapshot_base in url.parents:
            return url

        raise FileNotFoundError(url)

    def return_message(
            self, message="", content_type="text/plain",
            http_code=200, *headers):
        """Send ``message`` to the client"""
        self.send_response(http_code)
        self.send_header("WWW-Authenticate", "Basic realm=\"DoorPi\"")
        self.send_header("Server", metadata.distribution.metadata["Name"])
        self.send_header("Content-type", content_type)
        self.send_header("Connection", "close")
        for header in headers:
            self.send_header(*header)
        self.end_headers()
        self.wfile.write(
            message.encode("utf-8") if isinstance(message, str) else message)

    def check_authentication(self, parsed_path):
        """Perform authentication and authorization checks

        Raises:
            :class:`AuthenticationRequiredError` if authentication is
                required before access to the given path can be granted
        """
        try:
            public_resources = self.server.config["areas.public"]
            for public_resource in public_resources:
                if re.match(public_resource, parsed_path.path):
                    LOGGER.debug("public resource: %s", parsed_path.path)
                    return

            username, password = self.headers["authorization"] \
                .replace("Basic ", "").decode("base64").split(":", 1)

            user_session = self.server.sessions.get_session(username)
            if not user_session:
                user_session = self.server.sessions.build_security_object(
                    username, password)

            if not user_session:
                LOGGER.debug(
                    "need authentication (no session): %s", parsed_path.path)
                raise AuthenticationRequiredError()

            for write_permission in user_session["writepermissions"]:
                if re.match(write_permission, parsed_path.path):
                    LOGGER.info("user %s has write permissions: %s",
                                user_session["username"], parsed_path.path)
                    return

            for read_permission in user_session["readpermissions"]:
                if re.match(read_permission, parsed_path.path):
                    LOGGER.info("user %s has read permissions: %s",
                                user_session["username"], parsed_path.path)
                    return

            LOGGER.warning("user %s has no permissions: %s",
                           user_session["username"], parsed_path.path)
            raise AuthenticationRequiredError()
        except AuthenticationRequiredError:
            raise
        except Exception as err:
            LOGGER.exception("Error while authenticating a user")
            raise AuthenticationRequiredError() from err

    @staticmethod
    def _api_control(path, params):
        if len(path) != 2:
            raise BadRequestError()
        command = path[1]

        if command == "trigger_event":
            doorpi.INSTANCE.event_handler.fire_event(
                params["event"], params["source"], extra=params.get("extra"))
            result = {"success": True, "message": "Event was fired"}
        elif command == "config_value_get":
            try:
                key = params["key"][0]
            except (IndexError, KeyError) as err:
                raise BadRequestError() from err

            try:
                result = {
                    "success": True,
                    "message": doorpi.INSTANCE.config[key[0]],
                }
            except KeyError as err:
                result = {"success": False, "message": str(err)}
        elif command == "config_value_set":
            try:
                doorpi.INSTANCE.config[params["key"][0]] = params["value"][0]
            except (IndexError, KeyError, TypeError, ValueError) as err:
                result = {"success": False, "message": str(err)}
            else:
                result = {"success": True, "message": ""}
        elif command == "config_value_delete":
            try:
                key = params[key][0]
            except (IndexError, KeyError) as err:
                raise BadRequestError() from err

            try:
                del doorpi.INSTANCE.config[key]
            except KeyError as err:
                result = {"success": False, "message": str(err)}
            else:
                result = {"success": True, "message": ""}
        elif command == "config_save":
            try:
                doorpi.INSTANCE.config.save(params["configfile"])
            except KeyError as err:
                raise BadRequestError() from err
            else:
                result = {"success": True, "message": ""}
        else:
            raise BadRequestError()

        return (json_encoder.encode(result), "application/json")

    def _api_help(self, path, params):
        return self._resource(
            path.replace("/help", "/dashboard/parts"), params)

    def _api_mirror(self, path, params):
        message_parts = [
            "CLIENT VALUES:",
            "client_address=%s (%s)" % (
                self.client_address, self.address_string()),
            "raw_requestline=%s" % self.raw_requestline,
            "command=%s" % self.command,
            "path=%s" % self.path,
            "real path=%s" % path,
            "query=%s" % params,
            "request_version=%s" % self.request_version,
            "",
            "SERVER VALUES:",
            "server_version=%s" % self.server_version,
            "sys_version=%s" % self.sys_version,
            "protocol_version=%s" % self.protocol_version,
            "",
            "HEADERS RECEIVED:",
        ]
        for name, value in sorted(self.headers.items()):
            message_parts.append("%s=%s" % (name, value.rstrip()))
        message_parts.append("")
        message = "\r\n".join(message_parts)
        return (message, "text/plain")

    @staticmethod
    def _api_status(_, params):
        status = doorpi.INSTANCE.get_status(
            modules=params.get("modules", ""),
            name=params.get("name", ""),
            value=params.get("value", ""))
        return (json_encoder.encode(status.dictionary), "application/json")

    def _resource(self, path, params):
        """Serve a resource for the dashboard"""
        path = pathlib.PurePosixPath(path)

        if path.suffix in PARSABLE_FILE_EXTENSIONS:
            try:
                return (
                    self.environment.get_template(path.as_posix())
                    .render(
                        doorpi=doorpi.INSTANCE,
                        params=params,
                        code_min=("", ".min")[
                            LOGGER.getEffectiveLevel() <= logging.DEBUG],
                        proginfo="{} - version: {}".format(
                            metadata.distribution.metadata["Name"],
                            metadata.distribution.metadata["Version"]),
                    ),
                    "text/html")
            except jinja2.TemplateNotFound as err:
                raise FileNotFoundError(*err.args) from None
        else:
            return templates.get_resource(path)

    API_ENDPOINTS = {
        "control": "_api_control",
        "help": "_api_help",
        "mirror": "_api_mirror",
        "status": "_api_status",
    }


class SetAsTupleJSONEncoder(json.JSONEncoder):
    """A JSON encoder that encodes ``set()`` instances as tuples"""
    def default(self, o):
        if isinstance(o, (set, frozenset)):
            return tuple(o)
        return super().default(o)


json_encoder = SetAsTupleJSONEncoder()
