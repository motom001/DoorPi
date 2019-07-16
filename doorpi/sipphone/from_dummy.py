import logging

import doorpi

from doorpi.sipphone.abc import AbstractSIPPhone

logger = logging.getLogger(__name__)


def instantiate(): return DummyPhone()


class DummyPhone(AbstractSIPPhone):
    def get_name(self): return "dummy phone"

    def __init__(self):
        logger.info("Initializing dummy phone")
        eh = doorpi.DoorPi().event_handler
        for ev in ["OnSIPPhoneCreate", "OnSIPPhoneStart", "OnSIPPhoneDestroy"]:
            eh.register_event(ev, __name__)
        eh("OnSIPPhoneCreate", __name__)
        eh.register_action("OnShutdown", self.__del__)

    def __del__(self):
        logger.info("Deleting dummy phone")
        eh = doorpi.DoorPi().event_handler
        eh("OnSIPPhoneDestroy", __name__)
        eh.unregister_source(__name__, True)

    def start(self):
        logger.info("Starting dummy phone")
        doorpi.DoorPi().event_handler("OnSIPPhoneStart", __name__)

    def self_check(self):
        return

    def call(self, uri):
        logger.info("Starting call to %s", repr(uri))
        return False

    def dump_call(self):
        return {}

    def hangup(self):
        logger.info("Hanging up all calls")
        pass

    def is_admin(self, uri):
        return False
