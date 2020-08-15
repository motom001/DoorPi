import itertools
import logging
import time

import doorpi


LOGGER = logging.getLogger(__name__)
CONF_AREA_PREFIX = "AREA_"


class SessionHandler:

    _Sessions = {}

    @property
    def session_ids(self):
        return list(self._Sessions.keys())

    @property
    def sessions(self):
        return self._Sessions

    def __init__(self):
        doorpi.INSTANCE.event_handler.register_event("WebServerCreateNewSession", __name__)
        doorpi.INSTANCE.event_handler.register_event("WebServerAuthUnknownUser", __name__)
        doorpi.INSTANCE.event_handler.register_event("WebServerAuthWrongPassword", __name__)

    def destroy(self):
        doorpi.INSTANCE.event_handler.unregister_source(__name__, force=True)

    def get_session(self, session_id):
        if session_id in self._Sessions:
            LOGGER.trace("session %s found: %s", session_id, self._Sessions[session_id])
            return self._Sessions[session_id]
        LOGGER.trace("no session with session id %s found", session_id)
        return None

    __call__ = get_session

    def exists_session(self, session_id):
        return session_id in self._Sessions

    def build_security_object(self, username, password, remote_client=""):
        conf = doorpi.INSTANCE.config.view("web")

        try:
            real_password = conf["users", username]
        except KeyError:
            doorpi.INSTANCE.event_handler("WebServerAuthUnknownUser", __name__, {
                "username": username,
                "remote_client": remote_client
            })
            return None
        if real_password != password:
            doorpi.INSTANCE.event_handler("WebServerAuthWrongPassword", __name__, {
                "username": username,
                "password": password,
                "remote_client": remote_client
            })
            return None

        web_session = dict(
            username=username,
            remote_client=remote_client,
            session_starttime=time.time(),
            readpermissions=[],
            writepermissions=[],
            groups=[]
        )

        web_session["groups"] = {
            group for group, users in conf.view("groups").items()
            if username in users}
        read_areas = {
            area for area, groups in conf.view("readaccess").items()
            if web_session["groups"] & set(groups)}
        write_areas = (
            {area for area, groups in conf.view("writeaccess").items()
             if web_session["groups"] & set(groups)}
            - read_areas)

        web_session["readpermissions"] = frozenset(
            itertools.chain.from_iterable(
                conf["areas", area] for area in read_areas))
        web_session["writepermissions"] = frozenset(
            itertools.chain.from_iterable(
                conf["areas", area] for area in write_areas))
        web_session["readpermissions"] |= web_session["writepermissions"]

        doorpi.INSTANCE.event_handler("WebServerCreateNewSession", __name__, {
            "session": web_session
        })

        self._Sessions[web_session['username']] = web_session
        return web_session
