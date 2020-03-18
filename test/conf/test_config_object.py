import textwrap
from pathlib import Path

from doorpi.conf.config_object import ConfigObject

from ..mocks import DoorPiTestCase


class TestConfig(DoorPiTestCase):

    def setUp(self):
        super().setUp()
        Path("doorpi.ini").write_text(textwrap.dedent(f"""\
            [DoorPi]
            basepath = {Path.cwd()}
            """))

    def test_missing_file(self):
        ConfigObject("missingfile.ini")

    def test_write(self):
        conf = ConfigObject("doorpi.ini")
        conf.set_value("DoorPi", "basepath", Path.cwd())
        conf.save_config()

        self.assertEqual(f"[DoorPi]\nbasepath = {Path.cwd()}\n\n", Path("doorpi.ini").read_text())

    def test_get_nonexisting(self):
        conf = ConfigObject("doorpi.ini")
        self.assertEqual("somevalue", conf.get_string("DoorPi", "something", "somevalue"))

    def test_get_invalidfloat(self):
        conf = ConfigObject("doorpi.ini")
        with self.assertLogs("doorpi.conf.config_object", "ERROR"):
            self.assertEqual(200.0, conf.get_float("DoorPi", "basepath", 200.0))

    def test_get_invalidint(self):
        conf = ConfigObject("doorpi.ini")
        with self.assertLogs("doorpi.conf.config_object", "ERROR"):
            self.assertEqual(200, conf.get_int("DoorPi", "basepath", 200))

    def test_get_invalidbool(self):
        conf = ConfigObject("doorpi.ini")
        with self.assertLogs("doorpi.conf.config_object", "ERROR"):
            self.assertTrue(conf.get_bool("DoorPi", "basepath", True))
