import unittest

from unittest.mock import MagicMock

import doorpi.main


doorpi_instance = None


def DoorPi():
    global doorpi_instance

    if doorpi_instance is None:
        doorpi_instance = MagicMock()
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

    def tearDown(self):
        global doorpi_instance
        doorpi_instance = None


doorpi.main.add_trace_level()
