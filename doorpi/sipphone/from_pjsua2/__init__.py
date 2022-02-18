"""The PJSUA2 SIP phone module for DoorPi."""
import logging
from typing import Optional

import doorpi

EVENT_SOURCE = "sipphone.pjsua"
LOGGER = logging.getLogger(__name__)


def fire_event(
    event_name: str,
    async_only: bool = False,
    *,
    remote_uri: Optional[str] = None,
) -> None:
    """Helper function to ease firing events.

    Normally all DoorPi events are fired asynchronously, however this
    causes many short-lived event threads to appear. If one of these
    event threads calls into PJSUA2, it will permanently register the
    thread, effectively leaking memory over its life time.

    That is why events used internally by this module also fire a
    synchronous version, whose name is suffixed with "_S".
    """
    eh = doorpi.INSTANCE.event_handler
    extra = {"remote_uri": remote_uri} if remote_uri is not None else {}

    eh.fire_event(event_name, EVENT_SOURCE, extra=extra)
    if not async_only:
        eh.fire_event_sync(f"{event_name}_S", EVENT_SOURCE, extra=extra)
