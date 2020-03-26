import importlib
import logging
import time


LOGGER = logging.getLogger(__name__)
DEFAULT_MODULE_ATTR = ["__doc__", "__file__", "__name__", "__package__", "__path__", "__version__"]


try:
    import docutils.core
except ModuleNotFoundError:
    LOGGER.error("docutils not installed; dependency status in web interface will be incomplete")


def check_module_status(module):
    module["is_fulfilled"] = not module["fulfilled_with_one"]
    for module_name in module["libraries"]:
        status = {}
        try:
            package = importlib.import_module(module_name)
            content = dir(package)

            for attr in DEFAULT_MODULE_ATTR:
                if attr in content:
                    status[attr.replace("__", "")] = getattr(package, attr) or ""
                else:
                    status[attr.replace("__", "")] = "unknown"

            status["installed"] = True
            if module["fulfilled_with_one"]:
                module["is_fulfilled"] = True
            status["content"] = content

        except Exception as exp:
            status = {"installed": False, "error": str(exp)}
            if not module["fulfilled_with_one"]:
                module["is_fulfilled"] = False
        finally:
            module["libraries"][module_name]["status"] = status

    return module


def rsttohtml(rst):
    try:
        parts = docutils.core.publish_parts(rst, writer_name="html",
                                            settings_overrides={"input_encoding": "unicode"})
    except NameError:  # docutils not installed
        return "(cannot render text: docutils not installed)"
    return parts["fragment"]


def load_module_status(module_name):
    LOGGER.debug("Parsing requirements texts for %s", module_name)
    module = importlib.import_module(f"doorpi.status.requirements_lib.{module_name}").REQUIREMENT

    # parse reStructuredText descriptions to HTML:
    # the top-level module.text_description and _configuration
    for ent in ["text_description", "text_configuration"]:
        try:
            module[ent] = rsttohtml(module[ent])
            LOGGER.trace("Parsed %s.%s", module_name, ent)
        except KeyError:
            pass

    # module.libraries.*.[text_description, text_warning, text_test]
    for lib in module["libraries"].keys():
        for ent in ["text_description", "text_warning", "text_test", "text_configuration"]:
            try:
                module["libraries"][lib][ent] = rsttohtml(module["libraries"][lib][ent])
                LOGGER.trace("Parsed %s.libraries.%s.%s", module_name, lib, ent)
            except KeyError:
                pass
    # module.[configuration, events].*.description
    for ent in ["configuration", "events"]:
        try:
            for sub in range(len(module[ent])):
                try:
                    module[ent][sub]["description"] = rsttohtml(module[ent][sub]["description"])
                    LOGGER.trace("Parsed %s.%s.%s.description", module_name, ent, sub)
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
LOGGER.debug("Parsing requirements texts took %dms", int((time.time() - _STARTTIME) * 1000))
del _STARTTIME


def get(doorpi_obj, name, value):
    del doorpi_obj, value
    if not name: name = [""]

    status = {}
    for name_requested in name:
        for possible_name in REQUIREMENTS_DOORPI:
            if name_requested in possible_name:
                status[possible_name] = REQUIREMENTS_DOORPI[possible_name]

    return status


def is_active(doorpi_object):
    del doorpi_object
    return True
