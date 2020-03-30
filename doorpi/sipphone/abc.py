"""Abstract base class that helps implementing a SIP phone module."""
from abc import ABCMeta, abstractmethod


class AbstractSIPPhone(metaclass=ABCMeta):
    """Base class for all SIP phone modules

    This class defines and documents all public methods that a SIP
    phone module implementation should expose.
    """

    @abstractmethod
    def get_name(self) -> str:
        """Returns the name of this SIP phone module."""
        return None

    @abstractmethod
    def __init__(self):
        """Initializes the phone module.

        During __init__, the phone module should perform at least these
        steps:

        1. Register the events it may fire with the event handler
        2. Register itself for the "OnShutdown" event to perform cleanup
        3. Fire the "OnSipPhoneCreate" event

        A proper SIP phone module should register at least the following
        events:

        """

    @abstractmethod
    def start(self) -> None:
        """Start the phone module.

        Starting the phone module performs all steps necessary for
        DoorPi to make and receive calls.
        """

    @abstractmethod
    def stop(self):
        """Deinitializes the phone module and releases all resources."""

    @abstractmethod
    def call(self, uri: str) -> bool:
        """Make a call to the specified uri.

        This function should fire the "OnSipPhoneMakeCall" event before
        the call is made. The event should NOT be fired if another call
        to the same URI is already active or the given URI was invalid.

        Returns:
        - True if the call was made or another call to the same URI is
          already active
        - False otherwise
        """
        return False

    @abstractmethod
    def dump_call(self) -> dict:
        """Dumps information about the current call.

        Returns: A dict containing call information.
        The dict is either empty if no call is in progress,
        or it contains all of the following keys:
        - direction: Either "outgoing" or "incoming"
        - remote_uri: The URI of the connected remote
        - total_time: The amount of time this call has been active in seconds
        - camera: True if the call uses the camera
        """
        return {}

    @abstractmethod
    def hangup(self) -> None:
        """Hang up all currently active calls."""

    @abstractmethod
    def is_admin(self, uri: str) -> bool:
        """Check whether ``uri`` is registered as administrator."""
        return False
