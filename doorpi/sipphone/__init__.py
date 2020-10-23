"""The SIP phone container module for DoorPi.

A SIP phone module is required for DoorPi to make any outgoing calls
due to events (like a bell being rang), or to accept incoming calls.

The following requirements apply to all SIP phone modules:

- The module must be located at ``doorpi.sipphone.from_{name}``, where
  ``{name}`` is the name of the module. That same name is used in the
  configuration file to select the module.
- The top-level module must provide a function called ``instantiate()``,
  which takes no arguments and returns an instance of the phone module's
  base class.
- The phone module's base class must implement all instance methods of
  ``AbstractSIPPhone``. It is recommended that it inherits from the
  latter, however this is not a hard requirement.

A proper SIP phone module will fire these events during its life cycle:

- OnSIPPhoneCreate, OnSIPPhoneStart, OnSIPPhoneDestroy:
  These publish the module life cycle. They are fired by the abstract
  base class' respective methods, and are registered during its
  ``__init__()`` and unregistered during its ``stop()``. All other
  events mentioned here must be registered and fired manually.
- OnCallOutgoing:
  Fired when a call is started.
  Arguments:
    - "uri": The callee's URI as given (not canonicalized)
    - "canonical_uri": The callee's URI (canonicalized)
- OnCallConnect, OnCallDisconnect:
  Fired when a call is connected (picked up by remote) or disconnected
  (remote hung up), respectively.
  Arguments:
    - "uri": The remote end's URI (canonicalized)
- OnCallUnanswered:
  Fired when all outgoing calls went unanswered (or were rejected) by
  all recipients.
- OnCallTimeExceeded:
  Fired when a call was hung up because the maximum configured call
  time was exceeded, in addition to the regular OnCallDisconnect.
  Arguments:
    - "uri": The remote end's URI (canonicalized)
- OnCallIncoming:
  Fired when an external call comes in. This event is fired
  regardless of whether the call is accepted, rejected, or
  another call is already active.
  Arguments:
    - "uri": The caller's URI (canonicalized)
- OnCallAccepted:
  Fired when an incoming call is being accepted.
  Arguments:
    - "uri": The caller's URI (canonicalized)
- OnCallReject, OnCallBusy:
  Fired when an incoming call rejected due to the caller's URI
  not being a registered administrator or another call being
  currently active, respectively.
  Arguments:
    - "uri": The caller's URI (canonicalized)
- OnDTMF, OnDTMF_<seq>:
  Fired when the DTMF sequence ``<seq>`` was received.
"""
import importlib
import logging
import sys

import doorpi
from doorpi import metadata

from .abc import AbstractSIPPhone

__all__ = ["DEFAULT_MEDIA_DIR", "AbstractSIPPhone", "load"]

DEFAULT_MEDIA_DIR = "{}/share/{}".format(
    sys.prefix, metadata.distribution.metadata['Name'].lower())


def load() -> AbstractSIPPhone:
    sipphone_name = doorpi.INSTANCE.config["sipphone.type"]
    try:
        return (
            importlib.import_module(f"doorpi.sipphone.from_{sipphone_name}")
            .instantiate())  # type: ignore
    except ImportError as err:
        raise RuntimeError(
            f"Failed to load sip phone module {sipphone_name}"
        ) from err
