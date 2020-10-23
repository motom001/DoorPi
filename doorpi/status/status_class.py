from __future__ import annotations

import importlib
import json
import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence

import doorpi.doorpi

LOGGER = logging.getLogger(__name__)

MODULES = (
    "status_time",
    # "additional_informations",
    "config",
    "keyboard",
    "sipphone",
    "event_handler",
    "history_event",
    "history_snapshot",
    # "history_action",
    "environment",
    "webserver"
)


class DoorPiStatus:
    @property
    def json(self) -> str:
        return json.dumps(self.dictionary)

    @property
    def json_beautified(self) -> str:
        return json.dumps(self.dictionary, sort_keys=True, indent=4)

    def __init__(
            self, doorpi_obj: doorpi.doorpi.DoorPi,
            modules: Optional[Sequence[str]] = None,
            value: Optional[Sequence[str]] = (),
            name: Optional[Sequence[str]] = (),
            ) -> None:
        if not modules:
            modules = MODULES
        self.dictionary: Dict[str, Dict[str, Any]] = {}

        if len(modules) == 0:
            modules = MODULES

        for module in modules:
            if module not in MODULES:
                LOGGER.warning("Skipping unknown status module %s", module)
                continue
            try:
                getter_func = importlib.import_module(
                    f"doorpi.status.status_lib.{module}"
                ).get  # type: ignore
                self.dictionary[module] = getter_func(
                    doorpi_obj=doorpi_obj, name=name, value=value)
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception(
                    "Cannot collect status information for %s", module)
                self.dictionary[module] = {
                    "Error": f"Could not collect information about {module}"}


collect_status = DoorPiStatus  # pylint: disable=invalid-name
