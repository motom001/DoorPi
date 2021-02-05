"""Authentication and Authorization middlewares for DoorPiWeb"""
import dataclasses
import datetime
import re
import typing as T

import aiohttp.web
import pytz

import doorpi


def setup(app: aiohttp.web.Application) -> None:
    """Set up authentication and authorization for ``app``."""
    eh = doorpi.INSTANCE.event_handler
    eh.register_event("OnWebAuthLogin", "doorpi.web")
    eh.register_event("OnWebAuthUnknownUser", "doorpi.web")
    eh.register_event("OnWebAuthWrongPassword", "doorpi.web")
    app.middlewares.append(dpw_auth)
    app["doorpi_auth_sessions"] = {}


@dataclasses.dataclass
class Session:
    """Stores information about a session"""

    user: str
    groups: T.AbstractSet[str]
    remote: T.Optional[str]
    login_time: datetime.datetime
    readable: T.AbstractSet[str]
    writable: T.AbstractSet[str]


@aiohttp.web.middleware
async def dpw_auth(
    request: aiohttp.web.Request,
    handler: T.Callable[
        [aiohttp.web.Request], T.Awaitable[aiohttp.web.StreamResponse]
    ],
) -> aiohttp.web.StreamResponse:
    """The DoorPiWeb Authentication middleware"""
    if is_public_resource(request) or is_user_authorized(request):
        return await handler(request)
    else:
        return aiohttp.web.Response(
            text="401: Unauthorized",
            status=401,
            reason="UNAUTHORIZED",
            content_type="text/plain",
            headers={
                "WWW-Authenticate": 'Basic realm="DoorPi Web", charset="UTF-8"',
            },
        )


def is_public_resource(request: aiohttp.web.Request) -> bool:
    """Check whether the accessed resource is public"""
    if request.method != "GET":
        return False
    for res in request.app["doorpi_web_config"]["areas.public"]:
        if re.match(res, request.path):
            return True
    return False


def is_user_authorized(request: aiohttp.web.Request) -> bool:
    """Check if the logged in user is authorized for this request"""
    session = get_user_session(request)
    if session is None:
        return False

    if request.method == "GET":
        accessible = session.readable | session.readable
    else:
        accessible = session.writable

    cfg = request.app["doorpi_web_config"]

    for area in accessible:
        try:
            area_res = cfg["areas", area]
        except KeyError:
            continue

        for area_re in area_res:
            if re.fullmatch(area_re, request.path):
                return True
    return False


def get_user_session(
    request: aiohttp.web.Request,
) -> T.Optional[Session]:
    """Authenticate the user and return the session

    If the user cannot be authenticated, returns ``None``.
    """
    try:
        auth = request.headers["Authorization"]
    except KeyError:
        return None

    if not auth.startswith("Basic "):
        raise aiohttp.web.HTTPBadRequest()

    try:
        user, passwd = (
            auth[len("Basic ") :]
            .encode("ascii")
            .decode("base64")
            .split(":", 1)
        )
    except Exception:
        raise aiohttp.web.HTTPBadRequest() from None

    try:
        expected_passwd = request.app["doorpi_web_config"][("users", user)]
    except KeyError:
        doorpi.INSTANCE.event_handler.fire_event(
            "OnWebAuthUnknownUser",
            "doorpi.web",
            extra={"username": user, "remote_client": request.remote},
        )
        return None
    if passwd != expected_passwd:
        doorpi.INSTANCE.event_handler.fire_event(
            "OnWebAuthWrongPassword",
            "doorpi.web",
            extra={
                "username": user,
                "password": passwd,
                "remote_client": request.remote,
            },
        )
        return None

    session = request.app["doorpi_auth_sessions"].get(user)
    if session is None:
        session = create_session(user, request)
        request.app["doorpi_auth_sessions"][user] = session
        doorpi.INSTANCE.event_handler.fire_event(
            "OnWebAuthLogin",
            "doorpi.web",
            extra={"session": session},
        )
    return session


def create_session(username: str, request: aiohttp.web.Request) -> Session:
    """Create a new session for ``username``"""
    cfg = request.app["doorpi_web_conf"]
    usergroups = frozenset(
        group
        for group, users in cfg.view("groups").items()
        if username in users
    )
    readable = frozenset(
        area
        for area, groups in cfg.view("readaccess").items()
        if usergroups & groups
    )
    writable = frozenset(
        area
        for area, groups in cfg.view("writeaccess").items()
        if usergroups & groups
    )
    return Session(
        username,
        usergroups,
        request.remote,
        datetime.datetime.now(pytz.UTC),
        readable,
        writable,
    )
