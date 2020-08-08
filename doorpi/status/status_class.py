import importlib
import json
import logging

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
    def dictionary(self):
        return self.__status

    @property
    def json(self):
        return json.dumps(self.__status)

    @property
    def json_beautified(self):
        return json.dumps(self.__status, sort_keys=True, indent=4)

    def __init__(self, doorpi_obj, modules=MODULES, value=(), name=()):
        self.__status = {}
        self.collect_status(doorpi_obj, modules, value, name)

    def collect_status(self, doorpi_obj, modules=MODULES, value=(), name=()):
        if len(modules) == 0:
            modules = MODULES

        for module in modules:
            if module not in MODULES:
                LOGGER.warning("Skipping unknown status module %s", module)
                continue
            self.__status[module] = {}
            try:
                self.__status[module] = (
                    importlib
                    .import_module(f"doorpi.status.status_lib.{module}")
                    .get(doorpi_obj=doorpi_obj, name=name, value=value))
            except Exception:  # pylint: disable=broad-except
                LOGGER.exception(
                    "Cannot collect status information for %s", module)
                self.__status[module] = {
                    "Error": f"Could not collect information about {module}"}


collect_status = DoorPiStatus  # pylint: disable=invalid-name
