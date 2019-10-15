from ..mocks import DoorPiTestCase

import os
import textwrap

from doorpi.conf.config_object import ConfigObject

class TestConfig(DoorPiTestCase):

    def setUp(self):
        super().setUp()
        with open("doorpi.ini", "w") as f:
            f.write(textwrap.dedent(f"""\
                [DoorPi]
                basepath = {os.getcwd()}
                """))

    def test_missing_file(self):
        ConfigObject("missingfile.ini")

    def test_read(self):
        with open("doorpi.ini", "w") as f:
            f.write(textwrap.dedent(f"""\
                [DoorPi]
                basepath = {os.getcwd()}
                """))
        ConfigObject("doorpi.ini")

    def test_write(self):
        c = ConfigObject("doorpi.ini")
        c.set_value("DoorPi", "basepath", os.getcwd())
        c.save_config()

        with open("doorpi.ini", "r") as f:
            self.assertEqual(f.read().strip(), f"[DoorPi]\nbasepath = {os.getcwd()}")

    def test_get_nonexisting(self):
        c = ConfigObject("doorpi.ini")
        self.assertEqual(c.get_string("DoorPi", "something", "somevalue"), "somevalue")

    def test_get_invalidfloat(self):
        c = ConfigObject("doorpi.ini")
        with self.assertLogs("doorpi.conf.config_object", "ERROR"):
            self.assertEqual(c.get_float("DoorPi", "basepath", 200.0), 200.0)

    def test_get_invalidint(self):
        c = ConfigObject("doorpi.ini")
        with self.assertLogs("doorpi.conf.config_object", "ERROR"):
            self.assertEqual(c.get_int("DoorPi", "basepath", 200), 200)

    def test_get_invalidbool(self):
        c = ConfigObject("doorpi.ini")
        with self.assertLogs("doorpi.conf.config_object", "ERROR"):
            self.assertEqual(c.get_bool("DoorPi", "basepath", True), True)
