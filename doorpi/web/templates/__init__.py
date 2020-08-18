"""Templates and resources for DoorPiWeb"""
import mimetypes
import pathlib
from importlib import resources
from typing import Union


def get_resource(path: Union[str, pathlib.PurePosixPath]):
    """Get a resource and its MIME type"""
    path = pathlib.PurePosixPath("/", path)
    if path.name.startswith((".", "_")):
        raise FileNotFoundError()
    module = __name__ + path.parent.as_posix().replace("/", ".")

    try:
        res = resources.read_binary(module, path.name)
    except ModuleNotFoundError:
        raise FileNotFoundError() from None
    mime = mimetypes.guess_type(path.name, strict=False)
    return (res, mime[0])
