"""The DoorPiWeb request handler"""
from __future__ import annotations

import collections
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
from typing import (
    Any,
    Dict,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
    Union,
    cast,
)

import jinja2

import doorpi
from doorpi import metadata
from doorpi.actions import snapshot

from . import templates

LOGGER = logging.getLogger(__name__)

PARSABLE_FILE_EXTENSIONS = {".html"}
DOORPIWEB_SECTION = "DoorPiWeb"

_T = TypeVar("_T")
WebResource = Tuple[
    Union[bytes, str],  # Response body
    Optional[str],  # Content-Type
]


class ControlCommandResult(TypedDict):
    """The result of a control command"""

    success: bool
    message: str


class AuthenticationRequiredError(Exception):
    """Authentication is required to access this resource"""


class BadRequestError(Exception):
    """The received request was invalid"""


class DoorPiWebRequestHandler(http.server.BaseHTTPRequestHandler):
    """The DoorPiWeb request handler"""

    environment: jinja2.Environment
    server: doorpi.web.DoorPiWeb

    def log_error(
        self, format: str, *args: Any  # pylint: disable=redefined-builtin
    ) -> None:
        LOGGER.error(f"[%s] {format}", self.client_address[0], *args)

    def log_message(
        self, format: str, *args: Any  # pylint: disable=redefined-builtin
    ) -> None:
        LOGGER.debug(f"[%s] {format}", self.client_address[0], *args)

    @classmethod
    def prepare(cls) -> None:
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
    def destroy(cls) -> None:
        """Shut the request handlers down"""
        doorpi.INSTANCE.event_handler.unregister_source(__name__, force=True)
        del cls.environment

    def do_GET(self) -> None:  # pylint: disable=invalid-name
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
                path.path.split("/")[1], "_resource"
            )

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
    def list_directory(path: pathlib.Path) -> WebResource:
        """Serve a listing of the directory's contents"""
        dirs = []
        files = []
        for item in path.iterdir():
            if os.path.isfile(item):
                files.append(item)
            else:
                dirs.append(item)

        return_html = "".join(
            itertools.chain(
                (
                    '<!DOCTYPE html><html lang="en"><head></head>'
                    '<body><a href="..">..</a><br/>',
                ),
                (f'<a href="./{dir_}">{dir_}</a><br/>' for dir_ in dirs),
                (f'<a href="./{file}">{file}</a><br/>' for file in files),
                ("</body></html>",),
            )
        )
        return (return_html, "text/html")

    def return_redirection(self, location: str) -> None:
        """Serve a document that redirects to ``location``"""
        message = (
            "<html><head>"
            '<meta http-equiv="refresh" content="0;url={location}">'
            "</head><body>"
            '<a href="{location}">{location}</a>'
            "</body></html>"
        ).format(location=html.escape(location, True))
        self.return_message(message, "text/html", 307, ("Location", location))

    def canonicalize_filename(
        self, url: Union[str, pathlib.Path]
    ) -> pathlib.Path:
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
        self,
        message: Union[bytes, str] = "",
        content_type: str = "text/plain",
        http_code: int = 200,
        *headers: Tuple[str, str],
    ) -> None:
        """Send ``message`` to the client"""
        self.send_response(http_code)
        self.send_header("WWW-Authenticate", 'Basic realm="DoorPi"')
        self.send_header("Server", metadata.distribution.metadata["Name"])
        self.send_header("Content-type", content_type)
        self.send_header("Connection", "close")
        for header in headers:
            self.send_header(*header)
        self.end_headers()
        self.wfile.write(
            message.encode("utf-8") if isinstance(message, str) else message
        )

    def check_authentication(
        self, parsed_path: urllib.parse.ParseResult
    ) -> None:
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

            username, password = (
                self.headers["authorization"]
                .replace("Basic ", "")
                .decode("base64")
                .split(":", 1)
            )

            user_session = self.server.sessions.get_session(username)
            if not user_session:
                user_session = self.server.sessions.build_security_object(
                    username, password
                )

            if not user_session:
                LOGGER.debug(
                    "need authentication (no session): %s", parsed_path.path
                )
                raise AuthenticationRequiredError()

            for write_permission in user_session["writepermissions"]:
                if re.match(write_permission, parsed_path.path):
                    LOGGER.info(
                        "user %s has write permissions: %s",
                        user_session["username"],
                        parsed_path.path,
                    )
                    return

            for read_permission in user_session["readpermissions"]:
                if re.match(read_permission, parsed_path.path):
                    LOGGER.info(
                        "user %s has read permissions: %s",
                        user_session["username"],
                        parsed_path.path,
                    )
                    return

            LOGGER.warning(
                "user %s has no permissions: %s",
                user_session["username"],
                parsed_path.path,
            )
            raise AuthenticationRequiredError()
        except AuthenticationRequiredError:
            raise
        except Exception as err:
            LOGGER.exception("Error while authenticating a user")
            raise AuthenticationRequiredError() from err

    def _api_control(
        self, path: Sequence[str], params: Mapping[str, Sequence[Any]]
    ) -> WebResource:
        if len(path) != 2:
            raise BadRequestError()
        command = path[1]

        try:
            cmd_method = getattr(self, f"_api_command_{command}")
        except AttributeError:
            raise FileNotFoundError(command) from None
        result = cmd_method(params)
        return (json_encoder.encode(result), "application/json")

    @staticmethod
    def _api_control_trigger_event(
        params: Mapping[str, Sequence[Any]]
    ) -> ControlCommandResult:
        try:
            ev_name = _assert_value_type(params["event"][0], str)
            ev_source = _assert_value_type(params["source"][0], str)
            ev_extra: Optional[Dict[str, str]]
            if "extra" in params:
                ev_extra = _assert_value_type(params["extra"][0], dict)
                collections.deque(
                    (_assert_value_type(i, str) for i in ev_extra.values()), 0
                )
            else:
                ev_extra = None
        except (IndexError, TypeError) as err:
            raise BadRequestError() from err
        doorpi.INSTANCE.event_handler.fire_event(
            ev_name, ev_source, extra=ev_extra
        )
        return {"success": True, "message": "Event was fired"}

    @staticmethod
    def _api_control_config_value_get(
        params: Mapping[str, Any]
    ) -> ControlCommandResult:
        try:
            key = _assert_value_type(params["key"][0], str)
        except (IndexError, KeyError, TypeError) as err:
            raise BadRequestError() from err

        try:
            return {
                "success": True,
                "message": doorpi.INSTANCE.config[key[0]],
            }
        except KeyError as err:
            return {"success": False, "message": str(err)}

    @staticmethod
    def _api_control_config_value_set(
        params: Mapping[str, Any]
    ) -> ControlCommandResult:
        try:
            doorpi.INSTANCE.config[params["key"][0]] = params["value"][0]
        except (IndexError, KeyError, TypeError, ValueError) as err:
            return {"success": False, "message": str(err)}
        else:
            return {"success": True, "message": ""}

    @staticmethod
    def _api_control_config_value_delete(
        params: Mapping[str, Sequence[Any]]
    ) -> ControlCommandResult:
        try:
            key = params["key"][0]
        except (IndexError, KeyError) as err:
            raise BadRequestError() from err

        try:
            del doorpi.INSTANCE.config[key]
        except KeyError as err:
            return {"success": False, "message": str(err)}
        else:
            return {"success": True, "message": ""}

    @staticmethod
    def _api_control_config_save(
        params: Mapping[str, Sequence[Any]]
    ) -> ControlCommandResult:
        try:
            file = _assert_value_type(params["configfile"][0], str)
            doorpi.INSTANCE.config.save(file)
        except (KeyError, TypeError) as err:
            raise BadRequestError() from err
        else:
            return {"success": True, "message": ""}

    def _api_help(
        self, path: str, params: Mapping[str, Sequence[Any]]
    ) -> WebResource:
        return self._resource(
            path.replace("/help", "/dashboard/parts"), params
        )

    def _api_mirror(
        self, path: str, params: Mapping[str, Sequence[Any]]
    ) -> WebResource:
        message_parts = [
            "CLIENT VALUES:",
            "client_address=%s (%s)"
            % (self.client_address, self.address_string()),
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
    def _api_status(
        _: str, params: Mapping[str, Sequence[Any]]
    ) -> WebResource:
        try:
            modules = _assert_value_type(params.get("modules", [""])[0], str)
            names = _assert_value_type(params.get("name", [""])[0], str)
            values = _assert_value_type(params.get("value", [""])[0], str)
        except (IndexError, TypeError) as err:
            raise BadRequestError() from err

        status = doorpi.INSTANCE.get_status(
            modules=modules, name=names, value=values
        )
        return (json_encoder.encode(status.dictionary), "application/json")

    def _resource(
        self, rawpath: str, params: Mapping[str, Sequence[Any]]
    ) -> WebResource:
        """Serve a resource for the dashboard"""
        path = pathlib.PurePosixPath(rawpath)

        if path.suffix in PARSABLE_FILE_EXTENSIONS:
            try:
                return (
                    self.environment.get_template(path.as_posix()).render(
                        doorpi=doorpi.INSTANCE,
                        params=params,
                        code_min=("", ".min")[
                            LOGGER.getEffectiveLevel() <= logging.DEBUG
                        ],
                        proginfo="{} - version: {}".format(
                            metadata.distribution.metadata["Name"],
                            metadata.distribution.metadata["Version"],
                        ),
                    ),
                    "text/html",
                )
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

    def default(self, o: Any) -> Any:
        if isinstance(o, (set, frozenset)):
            return tuple(o)
        return super().default(o)


def _assert_value_type(value: Any, cls: Type[_T]) -> _T:
    if not isinstance(value, cls):
        raise TypeError(
            f"Invalid parameter type: {type(value)}, expected {cls}"
        )
    return value


json_encoder = SetAsTupleJSONEncoder()
