import contextlib
import os
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

from doorpi import config

doorpi_instance = None


def DoorPi():
    global doorpi_instance

    if doorpi_instance is None:
        doorpi_instance = MagicMock()
        doorpi_instance.config = config.Configuration()
        doorpi_instance.config.load_builtin_definitions()
        doorpi_instance.keyboard.input.return_value = False
        doorpi_instance.keyboard.output.return_value = True
        doorpi_instance.status = {}
        doorpi_instance.get_status.return_value = {}
        doorpi_instance.parse_string = MagicMock(wraps=lambda s: s)

    return doorpi_instance


class DoorPiTestCase(unittest.TestCase):
    def setUp(self):
        global doorpi_instance
        doorpi_instance = None
        self.tmpdir = TemporaryDirectory()
        self.oldpwd = os.getcwd()
        os.chdir(self.tmpdir.name)

    def tearDown(self):
        global doorpi_instance
        doorpi_instance = None
        os.chdir(self.oldpwd)
        self.tmpdir.cleanup()


@contextlib.contextmanager
def assert_no_raise(testcase, *, cls=Exception, msg="Exception was raised"):
    """Assert that the ``with`` block does not raise a ``cls`` instance"""
    try:
        yield
    except cls as err:
        raise testcase.failureException(msg) from err


@contextlib.contextmanager
def promise_deletion(obj, attr):
    """Delete ``obj.attr`` after the ``with`` block exits"""
    try:
        yield None
    finally:
        try:
            delattr(obj, attr)
        except AttributeError:
            pass
