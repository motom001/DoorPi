"""The dummy SIP phone module."""

import logging

import doorpi

from doorpi.actions import CallbackAction
from doorpi.sipphone.abc import AbstractSIPPhone

LOGGER = logging.getLogger(__name__)


class DummyPhone(AbstractSIPPhone):
    """A dummy SIP phone that does not actually place any calls."""

    def get_name(self):
        return "dummy phone"

    def __init__(self):
        super().__init__()
        LOGGER.info("Initializing dummy phone")
        eh = doorpi.DoorPi().event_handler
        for ev in ["OnSIPPhoneCreate", "OnSIPPhoneStart", "OnSIPPhoneDestroy"]:
            eh.register_event(ev, __name__)
        eh("OnSIPPhoneCreate", __name__)
        eh.register_action("OnShutdown", CallbackAction(self.stop))

    def stop(self):
        LOGGER.info("Deleting dummy phone")
        eh = doorpi.DoorPi().event_handler
        eh("OnSIPPhoneDestroy", __name__)
        eh.unregister_source(__name__, force=True)

    def start(self):
        LOGGER.info("Starting dummy phone")
        doorpi.DoorPi().event_handler("OnSIPPhoneStart", __name__)

    def call(self, uri):
        LOGGER.info("Starting call to %r", uri)
        return False

    def dump_call(self):
        return {}

    def hangup(self):
        LOGGER.info("Hanging up all calls")

    def is_admin(self, uri):
        return False


instantiate = DummyPhone  # pylint: disable=invalid-name
