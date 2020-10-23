"""The DoorPiWeb session handler"""
import itertools
import logging
import time
from typing import AbstractSet, Dict, Optional, TypedDict

import doorpi

LOGGER = logging.getLogger(__name__)


class DoorPiWebSession(TypedDict):
    username: str
    remote_client: str
    session_starttime: float
    readpermissions: AbstractSet[str]
    writepermissions: AbstractSet[str]
    groups: AbstractSet[str]


class SessionHandler:
    """The DoorPiWeb session handler"""
    def __init__(self) -> None:
        doorpi.INSTANCE.event_handler.register_event(
            "WebServerCreateNewSession", __name__)
        doorpi.INSTANCE.event_handler.register_event(
            "WebServerAuthUnknownUser", __name__)
        doorpi.INSTANCE.event_handler.register_event(
            "WebServerAuthWrongPassword", __name__)
        self.sessions: Dict[str, DoorPiWebSession] = {}

    @staticmethod
    def destroy() -> None:
        """Destroy the session handler"""
        doorpi.INSTANCE.event_handler.unregister_source(__name__, force=True)

    def get_session(self, session_id: str) -> Optional[DoorPiWebSession]:
        """Return the session identified by ``session_id``"""
        return self.sessions.get(session_id)

    __call__ = get_session

    def build_security_object(
            self, username: str, password: str, remote_client: str = "",
            ) -> Optional[DoorPiWebSession]:
        """Authenticate and authorize a user"""
        conf = doorpi.INSTANCE.config.view("web")

        try:
            real_password = conf["users", username]
        except KeyError:
            doorpi.INSTANCE.event_handler.fire_event(
                "WebServerAuthUnknownUser", __name__, extra={
                    "username": username,
                    "remote_client": remote_client,
                })
            return None
        if real_password != password:
            doorpi.INSTANCE.event_handler.fire_event(
                "WebServerAuthWrongPassword", __name__, extra={
                    "username": username,
                    "password": password,
                    "remote_client": remote_client,
                })
            return None

        web_session = DoorPiWebSession({
            "username": username,
            "remote_client": remote_client,
            "session_starttime": time.time(),
            "readpermissions": frozenset(),
            "writepermissions": frozenset(),
            "groups": frozenset(),
        })

        web_session["groups"] = {
            group for group, users in conf.view("groups").items()
            if username in users}
        read_areas = {
            area for area, groups in conf.view("readaccess").items()
            if web_session["groups"] & set(groups)}
        write_areas = {
            area for area, groups in conf.view("writeaccess").items()
            if web_session["groups"] & set(groups)}

        web_session["writepermissions"] = frozenset(
            map(str, itertools.chain.from_iterable(
                conf["areas", area] for area in write_areas)))
        web_session["readpermissions"] = frozenset(
            map(str, itertools.chain.from_iterable(
                conf["areas", area] for area in read_areas))
        ) | web_session["writepermissions"]

        doorpi.INSTANCE.event_handler(
            "WebServerCreateNewSession", __name__,
            extra={"session": web_session})

        self.sessions[web_session['username']] = web_session
        return web_session
