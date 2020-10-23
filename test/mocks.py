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
