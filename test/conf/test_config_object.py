import textwrap
from pathlib import Path

from ..mocks import DoorPiTestCase
from doorpi.conf.config_object import ConfigObject


class TestConfig(DoorPiTestCase):

    def setUp(self):
        super().setUp()
        Path("doorpi.ini").write_text(textwrap.dedent(f"""\
            [DoorPi]
            basepath = {Path.cwd()}
            """))

    def test_missing_file(self):
        ConfigObject("missingfile.ini")

    def test_read(self):
        with open("doorpi.ini", "w") as f:
            f.write(textwrap.dedent(f"""\
                [DoorPi]
                basepath = {Path.cwd()}
                """))
        ConfigObject("doorpi.ini")

    def test_write(self):
        c = ConfigObject("doorpi.ini")
        c.set_value("DoorPi", "basepath", Path.cwd())
        c.save_config()

        self.assertEqual(f"[DoorPi]\nbasepath = {Path.cwd()}\n\n", Path("doorpi.ini").read_text())

    def test_get_nonexisting(self):
        c = ConfigObject("doorpi.ini")
        self.assertEqual("somevalue", c.get_string("DoorPi", "something", "somevalue"))

    def test_get_invalidfloat(self):
        c = ConfigObject("doorpi.ini")
        with self.assertLogs("doorpi.conf.config_object", "ERROR"):
            self.assertEqual(200.0, c.get_float("DoorPi", "basepath", 200.0))

    def test_get_invalidint(self):
        c = ConfigObject("doorpi.ini")
        with self.assertLogs("doorpi.conf.config_object", "ERROR"):
            self.assertEqual(200, c.get_int("DoorPi", "basepath", 200))

    def test_get_invalidbool(self):
        c = ConfigObject("doorpi.ini")
        with self.assertLogs("doorpi.conf.config_object", "ERROR"):
            self.assertTrue(c.get_bool("DoorPi", "basepath", True))
