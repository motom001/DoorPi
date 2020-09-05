import importlib
import logging
import time


LOGGER = logging.getLogger(__name__)
DEFAULT_MODULE_ATTR = frozenset({
    "__doc__", "__file__", "__name__", "__package__", "__path__", "__version__"
})


try:
    import docutils.core
except ModuleNotFoundError:
    LOGGER.error("``docutils`` not installed, cannot render HTML descriptions")
    def rsttohtml(rst):
        return f"<pre>{rst}</pre>"
else:
    def rsttohtml(rst):
        return docutils.core.publish_parts(
            rst, writer_name="html",
            settings_overrides={"input_encoding": "unicode"}
        )["fragment"]


def check_module_status(module):
    module["is_fulfilled"] = not module.get("fulfilled_with_one")
    for module_name in module["libraries"]:
        status = {}
        try:
            package = importlib.import_module(module_name)
            content = dir(package)

            for attr in DEFAULT_MODULE_ATTR:
                if attr in content:
                    status[attr[2:-2]] = getattr(package, attr) or ""
                else:
                    status[attr[2:-2]] = "unknown"

            status["installed"] = True
            if module["fulfilled_with_one"]:
                module["is_fulfilled"] = True
            status["content"] = content

        except Exception as err:  # pylint: disable=broad-except
            status = {"installed": False, "error": str(err)}
            if not module["fulfilled_with_one"]:
                module["is_fulfilled"] = False
        finally:
            module["libraries"][module_name]["status"] = status

    return module


def load_module_status(module_name):
    LOGGER.debug("Parsing requirements texts for %s", module_name)
    module = importlib.import_module(
        f"doorpi.status.requirements_lib.{module_name}"
    ).REQUIREMENT

    # parse reStructuredText descriptions to HTML:
    # the top-level module.text_description and _configuration
    for ent in ("text_description", "text_configuration"):
        try:
            module[ent] = rsttohtml(module[ent])
            LOGGER.trace("Parsed %s.%s", module_name, ent)
        except KeyError:
            pass

    # module.libraries.*.[text_description, text_warning, text_test]
    for lib_name, lib_req in module.setdefault("libraries", {}).items():
        for ent in lib_req:
            if ent.startswith("text_"):
                lib_req[ent] = rsttohtml(lib_req[ent])
                LOGGER.trace(
                    "Parsed %s.libraries.%s.%s", module_name, lib_name, ent)

    # module.[configuration, events].*.description
    for ent in ("configuration", "events"):
        try:
            for sub in range(len(module.setdefault(ent, []))):
                try:
                    module[ent][sub]["description"] = rsttohtml(
                        module[ent][sub]["description"])
                    LOGGER.trace(
                        "Parsed %s.%s.%s.description", module_name, ent, sub)
                except KeyError:
                    pass
        except KeyError:
            pass

    return check_module_status(module)


_STARTTIME = time.time()
REQUIREMENTS_DOORPI = {
    "config": load_module_status("req_config"),
    "sipphone": load_module_status("req_sipphone"),
    "event_handler": load_module_status("req_event_handler"),
    "webserver": load_module_status("req_webserver"),
    "keyboard": load_module_status("req_keyboard"),
    "system": load_module_status("req_system")
}
LOGGER.debug(
    "Parsing requirements texts took %dms",
    int((time.time() - _STARTTIME) * 1000))
del _STARTTIME


def get(doorpi_obj, name, value):
    del doorpi_obj, value
    if not name:
        name = [""]

    status = {}
    for name_requested in name:
        for possible_name in REQUIREMENTS_DOORPI:
            if name_requested in possible_name:
                status[possible_name] = REQUIREMENTS_DOORPI[possible_name]

    return status


def is_active(doorpi_object):
    del doorpi_object
    return True
