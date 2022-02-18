"""Templates and resources for DoorPiWeb"""
import mimetypes
import pathlib
from importlib import resources
from typing import Callable, Optional, Tuple, TypeVar, Union

import jinja2

_T = TypeVar("_T")


class DoorPiWebTemplateLoader(jinja2.BaseLoader):
    """The Jinja2 template loader for DoorPiWeb"""

    def get_source(
        self,
        environment: jinja2.Environment,
        template: str,
    ) -> Tuple[str, Optional[str], Callable[[], bool]]:
        try:
            _, resource = _get_resource(template, resources.read_text)
        except FileNotFoundError:
            raise jinja2.TemplateNotFound(template) from None
        return (resource, None, lambda: False)


def get_resource(
    path: Union[str, pathlib.PurePosixPath]
) -> Tuple[bytes, Optional[str]]:
    """Get a resource and its MIME type"""
    name, resource = _get_resource(path, resources.read_binary)
    mime = mimetypes.guess_type(name, strict=False)
    return (resource, mime[0])


def _get_resource(
    path: Union[str, pathlib.PurePosixPath], load: Callable[[str, str], _T], /
) -> Tuple[str, _T]:
    path = pathlib.PurePosixPath("/", path)
    if path.name.startswith((".", "_")):
        raise FileNotFoundError()
    module = (__name__ + path.parent.as_posix().replace("/", ".")).rstrip(".")

    try:
        resource = load(module, path.name)
    except ModuleNotFoundError:
        raise FileNotFoundError() from None
    return (path.name, resource)
