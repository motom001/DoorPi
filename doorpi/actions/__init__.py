"""Actions that DoorPi can perform in response to events.

Submodules of ``doorpi.actions`` implement actions usable from the
configuration file. An action instantiator must be tagged with the
``@action(ac_name)`` decorator in order to be recognized. The
instantiator is passed the parameters defined in the configuration
file, and it must return a Callable which will be called to fire
the action. The returned Callable must take two parameters; the
Event ID (a string that uniquely identifies the currently handled
event) and a dict of extra data. When an action performs any log
output, it should prepend its messages with ``[EVENT_ID]``. What kind
of extra data is passed depends on the actual event being handled.

When loading DoorPi, all submodules of ``doorpi.actions`` will be
imported and the ``@action``s defined therein registered with the
dispatcher. Modules that fail to import are logged and skipped. This
is so that if a module requires extra dependencies that are not
currently available, only the actions it defines will be unusable,
but the rest of DoorPi still functions as normal.

For more details of the required methods on action classes, see the
definition of `Action` below.
"""
from __future__ import annotations

import abc
import importlib.util
import logging
import pkgutil
from typing import (
    Any,
    Callable,
    Dict,
    Mapping,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
)

import doorpi

LOGGER = logging.getLogger(__name__)
ACTION_REGISTRY = {}

_T = TypeVar("_T", bound=Callable)


def action(name: str) -> Callable[[_T], _T]:
    """Tag a callable as action instantiator"""

    def register_action(func: _T) -> _T:
        if ":" in name:
            raise ValueError(f"Invalid action name {name}")
        if name in ACTION_REGISTRY:
            raise ValueError(f"Non-unique action name {name}")
        ACTION_REGISTRY[name] = func
        return func

    return register_action


def from_string(confstr: str) -> Optional[Action]:
    """Instantiates an action from a configuration string."""
    atype = confstr.split(":")[0]
    if not atype:
        return None
    if atype not in ACTION_REGISTRY:
        raise ValueError(f"Unknown action {atype!r}")
    args = confstr[len(atype) + 1 :]
    arglist = args.split(",") if len(args) > 0 else []
    return ACTION_REGISTRY[atype](*arglist)


@runtime_checkable
class Action(Protocol, metaclass=abc.ABCMeta):
    """Abstract base class that defines an action's interface."""

    @abc.abstractmethod
    def __init__(self, *args: str) -> None:
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
        super().__init__()

    @abc.abstractmethod
    def __call__(self, event_id: str, extra: Mapping[str, Any]) -> None:
        """Execute the action.

        Arguments:
        - `event_id`: The unique event ID. Log messages emitted by
                      actions should be prepended with "[event_id]".
        - `extra`: A dict containing additional information from the
                   event source, as well as runtime information about
                   the last time this event was fired.
        """

    @abc.abstractmethod
    def __str__(self) -> str:
        """A human readable representation of this action

        str(some_action) should result in a human-readable string that
        accurately describes the action, which will be used in user
        facing applications (e.g. logs or the web UI).
        """
        return ""

    @abc.abstractmethod
    def __repr__(self) -> str:
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

    def __init__(
        self,
        callback: Callable[..., Any],
        *args: Any,
        **kw: Any,
    ) -> None:
        super().__init__()
        if not callable(callback):
            raise ValueError("Callback must be callable")
        self._callback = callback
        self._args = args
        self._kw = kw

    def __call__(self, event_id: str, extra: Mapping[str, Any]) -> None:
        del event_id, extra
        self._callback(*self._args, **self._kw)

    def __str__(self) -> str:
        return f"{self.__class__.__name__} for {self._callback!r}"

    def __repr__(self) -> str:
        return (
            "<internal callback to"
            f" {self._callback!r} (args={self._args}, kwargs={self._kw})>"
        )


class CheckAction(CallbackAction):
    """A CallbackAction which aborts program execution on errors.

    Callbacks wrapped by this action are expected to raise an
    appropriate exception in case an internal error is detected. The
    exception will be logged and DoorPi will shut down.
    """

    def __call__(self, event_id: str, extra: Mapping[str, Any]) -> None:
        try:
            super().__call__(event_id, extra)
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("[%s] *** Internal self check failed", event_id)
            doorpi.INSTANCE.doorpi_shutdown()

    def __repr__(self) -> str:
        return f"<internal self-check with {self._callback!r}>"


module = _ = None
spec = importlib.util.find_spec(__name__)
assert spec is not None
for _, module, _ in pkgutil.iter_modules(
    spec.submodule_search_locations or [], f"{__name__}."
):
    try:
        importlib.import_module(module)
    except Exception as exc:  # pylint: disable=broad-except
        LOGGER.error(
            "Unable to load actions from %s: %s: %s",
            module,
            exc.__class__.__name__,
            exc,
        )
if module is None:
    raise RuntimeError("Could not load any action modules")
del module, spec, _
