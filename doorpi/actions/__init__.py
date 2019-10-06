from abc import ABCMeta, abstractmethod


class Action(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, *args):
        """Construct the action with the given arguments.

        Arguments are taken from the config file and split at commas.
        __init__ should validate the passed arguments (as far as
        reasonable), in order to detect configuration errors as soon
        as possible.

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
        constructed this action, or a string equal to that.
        For actions which cannot be serialized that way,
        a string beginning with "<internal " should be returned.
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
        return f"CallbackAction for {self.__callback!r} (args={self.__args}, kwargs={self.__kw})"

    def __repr__(self):
        return "<internal callback to" \
               f" {self.__callback!r} (args={self.__args}, kwargs={self.__kw})>"


def from_string(s):
    import importlib

    atype = s.split(":")[0]
    if not atype: return None
    if atype.startswith("_"):
        raise ValueError("Action types cannot start with an underscore")
    args = s[len(atype) + 1:].split(",")

    try:
        return importlib.import_module(f"doorpi.actions.{atype}").instantiate(*args)
    except ImportError as err:
        raise RuntimeError(f"Unable to instantiate {atype} action") from err
    except Exception as ex:
        raise RuntimeError(f"Error creating action from config: {s}") from ex
