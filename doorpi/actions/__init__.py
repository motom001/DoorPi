"""Actions that DoorPi can perform in response to events.

Submodules of `doorpi.actions` implement actions usable from the
configuration file. The module name is used to determine the action's
name in the configuration file. Example: `doorpi.actions.out` is
configured as `out:<params>`.

Each submodule must provide a top-level callable named `instantiate`,
which will be passed all parameters specified in the configuration file,
and must return a concrete subclass of `Action` (the abstract base class
defined in this file). For more details see `Action.__init__` below.

For more details of the required methods on action classes, see the
definition of `Action` below.
"""

from abc import ABCMeta, abstractmethod

import logging
import doorpi


logger = logging.getLogger(__name__)


class Action(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, *args):
        """Construct the action with the given arguments.

        Arguments are taken from the config file and split at commas.
        Since all arguments are passed as `str`, `__init__` should
        validate the passed arguments (as far as reasonable), in order
        to detect configuration errors as soon as possible.

        If the action intends to take the entire argument string as
        one, without handling commas specially, it must rejoin the
        given arguments again like so:

            def __init__(self, *args):
                argstring = ",".join(args)
        """
        pass

    @abstractmethod
    def __call__(self, event_id, extra):
        """Execute the action.

        Arguments:
        - `event_id`: The unique event ID. Log messages emitted by
                      actions should be prepended with "[event_id]".
        - `extra`: A dict containing additional information from the
                   event source, as well as runtime information about
                   the last time this event was fired.
        """
        pass

    @abstractmethod
    def __str__(self):
        """A human readable representation of this action

        str(some_action) should result in a human-readable string that
        accurately describes the action, which will be used in user
        facing applications (e.g. logs or the web UI).
        """
        return None

    @abstractmethod
    def __repr__(self):
        """Form an action string

        repr(some_action) should reassemble the string which originally
        constructed this action, or a string equal to that. For actions
        which cannot be serialized that way, a string beginning with
        "<internal " should be returned.
        """
        return ""


class CallbackAction(Action):
    """An action that executes a callback.

    This is used to facilitate programming of other modules. It is used
    to wrap functions or (bound) methods, so that they can be executed
    in response to a certain event by the event manager.
    """

    def __init__(self, callback, *args, **kw):
        if not callable(callback):
            raise ValueError("Callback must be callable")
        self.__callback = callback
        self.__args = args
        self.__kw = kw

    def __call__(self, event_id, extra):
        self.__callback(*self.__args, **self.__kw)

    def __str__(self):
        return f"{self.__class__.__name__} for {self.__callback!r}"

    def __repr__(self):
        return "<internal callback to" \
               f" {self.__callback!r} (args={self.__args}, kwargs={self.__kw})>"


class CheckAction(CallbackAction):
    """A CallbackAction which aborts program execution on errors.

    Callbacks wrapped by this action are expected to raise an
    appropriate exception in case an internal error is detected. The
    exception will be logged and DoorPi will shut down.
    """

    def __call__(self, event_id, extra):
        try:
            super().__call__(event_id, extra)
        except Exception:
            logger.exception("[%s] *** UNCAUGHT EXCEPTION: Internal self check failed", event_id)
            doorpi.DoorPi().doorpi_shutdown()

    def __repr__(self):
        return f"<internal self-check with {self._CallbackAction__callback!r}>"


def from_string(s):
    import importlib

    atype = s.split(":")[0]
    if not atype: return None
    if atype.startswith("_"):
        raise ValueError("Action types cannot start with an underscore")
    args = s[len(atype) + 1:]
    args = args.split(",") if len(args) > 0 else []

    try:
        return importlib.import_module(f"doorpi.actions.{atype}").instantiate(*args)
    except ImportError as err:
        raise RuntimeError(f"Unable to instantiate {atype} action") from err
    except Exception as ex:
        raise RuntimeError(f"Error creating action from config: {s}") from ex
