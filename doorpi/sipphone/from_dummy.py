"""The dummy SIP phone module."""

import logging

import doorpi
from doorpi.actions import CallbackAction
from doorpi.sipphone.abc import AbstractSIPPhone

LOGGER = logging.getLogger(__name__)


class DummyPhone(AbstractSIPPhone):
    """A dummy SIP phone that does not actually place any calls."""

    def get_name(self) -> str:  # pragma: no cover
        return "dummy phone"

    def __init__(self) -> None:
        super().__init__()
        LOGGER.info("Initializing dummy phone")
        eh = doorpi.INSTANCE.event_handler
        for ev in ("OnSIPPhoneCreate", "OnSIPPhoneStart", "OnSIPPhoneDestroy"):
            eh.register_event(ev, __name__)
        eh("OnSIPPhoneCreate", __name__)
        eh.register_action("OnShutdown", CallbackAction(self.stop))

    def stop(self) -> None:
        LOGGER.info("Deleting dummy phone")
        eh = doorpi.INSTANCE.event_handler
        eh("OnSIPPhoneDestroy", __name__)
        eh.unregister_source(__name__, force=True)

    def start(self) -> None:
        LOGGER.info("Starting dummy phone")
        doorpi.INSTANCE.event_handler("OnSIPPhoneStart", __name__)

    def call(self, uri: str) -> bool:
        LOGGER.info("Starting call to %r", uri)
        return False

    def dump_call(self) -> dict:  # pragma: no cover
        return {}

    def hangup(self) -> None:
        LOGGER.info("Hanging up all calls")

    def is_admin(self, uri: str) -> bool:
        return False
