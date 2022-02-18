import datetime
import enum
import io
import operator
import pathlib
import tempfile
import textwrap

from doorpi import config

from ..mocks import DoorPiTestCase, assert_no_raise, promise_deletion


class TestConfigDefs(DoorPiTestCase):
    def test_attached_defs_can_be_retrieved(self):
        keydef = {
            "testkey": {"_type": "string", "_default": "foo"},
            "testns": {
                "testns2": {
                    "testkey": {"_default": 3},
                    "testkey2": {"_default": -7.8},
                }
            },
        }

        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydef})

        with self.subTest("Top-level"):
            actual, _ = conf_obj.keydef("testkey")
            for key, val in keydef["testkey"].items():
                if key == "_type":
                    continue
                with self.subTest(key=key):
                    self.assertEqual(val, actual[key])

        with self.subTest("Nested 1"):
            actual, _ = conf_obj.keydef("testns.testns2.testkey")
            for key, val in keydef["testns"]["testns2"]["testkey"].items():
                if key == "_type":
                    continue
                with self.subTest(key=key):
                    self.assertEqual(val, actual[key])

        with self.subTest("Nested 2"):
            actual, _ = conf_obj.keydef("testns.testns2.testkey2")
            for key, val in keydef["testns"]["testns2"]["testkey2"].items():
                if key == "_type":
                    continue
                with self.subTest(key=key):
                    self.assertEqual(val, actual[key])

    def test_attaching_defs_creates_type_object(self):
        keydef = {
            "testkey": {"_type": "string"},
        }

        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydef})
        actual, _ = conf_obj.keydef("testkey")

        self.assertIsInstance(actual["_type"], config.types.String)

    def test_attaching_enum_def_reuses_existing_enum(self):
        keydef = {
            "config": {
                "test_key": {
                    "_type": "enum",
                    "_enumcls": "doorpi.config.TestKey",
                    "_default": "bar",
                }
            }
        }

        class TestKey(enum.Enum):
            foo = enum.auto()
            bar = enum.auto()
            baz = enum.auto()

        config.TestKey = TestKey

        with promise_deletion(config, "TestKey"):
            conf_obj = config.Configuration()
            conf_obj.attach_defs({"config": keydef})

            self.assertIs(TestKey, TestKey)
            keydef, _ = conf_obj.keydef("config.test_key")
            self.assertIs(TestKey.foo, keydef["_type"].insertcast("foo"))


class TestConfigLoadSave(DoorPiTestCase):
    def test_config_can_be_loaded_from_file_given_as_str(self):
        keydef = {"testkey": {"_default": "foo"}}
        conffile = "testkey = 'bar'"
        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydef})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = pathlib.Path(tmpdir, "config.toml")
            path.write_text(conffile)

            with assert_no_raise(self):
                conf_obj.load(str(path))

    def test_config_can_be_loaded_from_file_given_as_path(self):
        keydef = {"testkey": {"_default": "foo"}}
        conffile = "testkey = 'bar'"
        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydef})

        with tempfile.TemporaryDirectory() as tmpdir:
            path = pathlib.Path(tmpdir, "config.toml")
            path.write_text(conffile)

            with assert_no_raise(self):
                conf_obj.load(path)

    def test_config_can_be_loaded_from_filelike(self):
        keydef = {"testkey": {"_default": "foo"}}
        conffile = "testkey = 'bar'"
        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydef})

        with assert_no_raise(self):
            conf_obj.load(io.StringIO(conffile))

    def test_config_can_be_saved_to_file_given_as_str(self):
        conf_obj = config.Configuration()
        with tempfile.TemporaryDirectory() as tmpdir:
            with assert_no_raise(self):
                conf_obj.save(str(pathlib.Path(tmpdir, "config.toml")))

    def test_config_can_be_saved_to_file_given_as_path(self):
        conf_obj = config.Configuration()
        with tempfile.TemporaryDirectory() as tmpdir:
            with assert_no_raise(self):
                conf_obj.save(pathlib.Path(tmpdir, "config.toml"))

    def test_config_can_be_saved_to_filelike(self):
        conf_obj = config.Configuration()
        target = io.StringIO()
        with assert_no_raise(self):
            conf_obj.save(target)

    def test_loading_and_saving_results_in_same_file(self):
        expected = io.StringIO(
            textwrap.dedent(
                """\
            testkey = "Testvalue"

            [testsection]
            testkey2 = 7
            """
            )
        )
        keydefs = {
            "testkey": {"_type": "string"},
            "testsection": {
                "testkey2": {"_type": "int"},
            },
        }

        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydefs})
        conf_obj.load(expected)

        actual = io.StringIO()
        conf_obj.save(actual)

        self.assertEqual(expected.getvalue(), actual.getvalue())

    def test_loading_builtin_definitions_does_not_raise(self):
        conf_obj = config.Configuration()
        with assert_no_raise(self):
            conf_obj.load_builtin_definitions()


class TestConfigGetSet(DoorPiTestCase):
    def test_setting_invalid_value_type_raises(self):
        values = [
            ("int", "0"),
            ("int", 1.5),
            ("int", [0]),
            ("float", "0"),
            ("float", [1.5]),
            ("bool", 7),
            ("bool", "why, of course"),
            ("string", ["foo"]),
        ]
        for type_, value in values:
            with self.subTest(type=type_, value=value):
                conf_obj = config.Configuration()
                conf_obj.attach_defs(
                    {
                        "config": {
                            "testkey": {"_type": type_},
                        }
                    }
                )
                with self.assertRaises((TypeError, ValueError)):
                    conf_obj["testkey"] = value

    def test_set_values_can_be_retrieved(self):
        conf_obj = config.Configuration()
        conf_obj.attach_defs(
            {
                "config": {
                    "testkey": {"_type": "string"},
                }
            }
        )

        conf_obj["testkey"] = "foo"
        self.assertEqual("foo", conf_obj["testkey"])

    def test_loaded_non_enum_values_can_be_retrieved(self):
        values = [
            ("int", "1", 1),
            ("float", "1.5", 1.5),
            ("bool", "true", True),
            ("string", '"teststring"', "teststring"),
            ("date", "2020-01-20", datetime.date(2020, 1, 20)),
            ("time", "01:30:59", datetime.time(1, 30, 59)),
            (
                "datetime",
                "2020-01-20T01:30:59",
                datetime.datetime(2020, 1, 20, 1, 30, 59),
            ),
            ("list", "['foo', 'bar', 'baz']", ("foo", "bar", "baz")),
            ("path", '"/tmp"', pathlib.Path("/tmp")),
        ]
        for type_, configval, expected in values:
            with self.subTest(type=type_, value=configval):
                conf_obj = config.Configuration()
                conf_obj.attach_defs(
                    {
                        "config": {
                            "testkey": {"_type": type_},
                        }
                    }
                )
                conf_obj.load(io.StringIO(f"testkey = {configval!s}"))

                actual = conf_obj["testkey"]
                self.assertIsInstance(actual, type(expected))
                self.assertEqual(actual, expected)

    def test_loaded_enums_can_be_retrieved(self):
        class TestKey(enum.Enum):
            foo = enum.auto()
            bar = enum.auto()
            baz = enum.auto()

        keydef = {
            "config": {
                "test_key": {
                    "_type": "enum",
                    "_enumcls": "doorpi.config.TestKey",
                    "_default": "bar",
                }
            }
        }
        conffile = textwrap.dedent(
            """\
            [config]
            test_key = 'baz'
            """
        )

        with promise_deletion(config, "TestKey"):
            config.TestKey = TestKey
            conf_obj = config.Configuration()
            conf_obj.attach_defs({"config": keydef})
            conf_obj.load(io.StringIO(conffile))

            actual = conf_obj["config.test_key"]
            self.assertIs(actual, config.TestKey.baz)

    def test_setting_castable_value_autocasts(self):
        values = [
            ("float", 1, float(1)),
            ("bool", "true", True),
            ("bool", "yes", True),
            ("bool", "on", True),
            ("bool", "1", True),
            ("bool", 1, True),
            ("bool", "false", False),
            ("bool", "no", False),
            ("bool", "off", False),
            ("bool", "0", False),
            ("bool", 0, False),
            ("string", 0, "0"),
            ("string", 3.5, str(3.5)),
            ("string", True, "True"),
            ("string", datetime.date(2020, 1, 20), "2020-01-20"),
            ("string", datetime.time(1, 30, 59), "01:30:59"),
            (
                "string",
                datetime.datetime(2020, 1, 20, 1, 30, 59),
                "2020-01-20 01:30:59",
            ),
            ("path", "/tmp", pathlib.Path("/tmp")),
        ]
        for type_, testvalue, expected in values:
            with self.subTest(type=type_, value=testvalue):
                conf_obj = config.Configuration()
                conf_obj.attach_defs(
                    {
                        "config": {
                            "testkey": {"_type": type_},
                        }
                    }
                )
                conf_obj["testkey"] = testvalue

                self.assertEqual(expected, conf_obj["testkey"])

    def test_reading_key_without_default_value_raises_KeyError(self):
        conf_obj = config.Configuration()
        conf_obj.attach_defs(
            {
                "config": {
                    "testkey": {"_type": "string"},
                }
            }
        )

        self.assertRaises(KeyError, operator.itemgetter("testkey"), conf_obj)


class TestConfigKeydef(DoorPiTestCase):
    def test_getting_keydef_of_namespace_raises_KeyError(self):
        keydef = {"namespace": {"key": {"_default": True}}}
        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydef})
        self.assertRaises(KeyError, conf_obj.keydef, "namespace")

    def test_too_long_key_path_raises_KeyError(self):
        keydef = {"namespace": {"key": {"_default": True}}}
        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydef})
        self.assertRaises(KeyError, conf_obj.keydef, "namespace.key.sub")

    def test_getting_keydef_of_nonexistent_key_raises_KeyError(self):
        keydef = {"namespace": {"key": {"_default": True}}}
        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydef})
        self.assertRaises(KeyError, conf_obj.keydef, "namespace.boo")

    def test_star_segments_are_wildcards(self):
        keydef = {"namespace": {"*": {"_default": True}}}
        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydef})
        _, wildsegments = conf_obj.keydef("namespace.key")
        self.assertEqual(wildsegments, ["key"])


class ConfigView(DoorPiTestCase):
    def test_iterates_over_keys_with_values(self):
        keydef = {
            "namespace": {
                "key1": {"_default": True},
                "key2": {"_default": "foo"},
                "key3": {"subkey": {"_default": 10}},
            }
        }
        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydef})
        conf_obj.load(
            io.StringIO(
                textwrap.dedent(
                    """\
            [namespace]
            key1 = false
            key2 = "bar"
            key3 = {subkey = 3}
            """
                )
            )
        )

        self.assertEqual(
            set(conf_obj.view("namespace")), set(keydef["namespace"].keys())
        )

    def test_does_not_iterate_over_unset_keys(self):
        keydef = {
            "namespace": {
                "key1": {"_default": True},
                "key2": {"_default": "foo"},
                "key3": {"subkey": {"_default": 10}},
            }
        }
        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydef})

        self.assertEqual(set(conf_obj.view("namespace")), set())

    def test_cannot_iterate_over_valuekeys(self):
        keydef = {
            "namespace": {
                "key1": {"_default": True},
                "key2": {"_default": "foo"},
                "key3": {"subkey": {"_default": 10}},
            }
        }
        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydef})

        with self.assertRaises(KeyError):
            iter(conf_obj.view("namespace.key1"))

    def test_returns_number_of_keys_as_len(self):
        keydef = {
            "namespace": {
                "key1": {"_default": True},
                "key2": {"_default": "foo"},
                "key3": {"subkey": {"_default": 10}},
            }
        }
        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydef})
        conf_obj.load(
            io.StringIO(
                textwrap.dedent(
                    """\
            [namespace]
            key1 = false
            key2 = "bar"
            key3 = {subkey = 3}
            """
                )
            )
        )

        self.assertEqual(len(conf_obj.view("namespace")), 3)

    def test_can_get_values_from_source_configuration(self):
        keydef = {"namespace": {"key": {"_default": "foo"}}}
        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydef})

        view = conf_obj.view("namespace")
        conf_obj["namespace.key"] = "bar"

        self.assertEqual(view["key"], "bar")

    def test_can_set_values_on_source_configuration(self):
        keydef = {"namespace": {"key": {"_default": "foo"}}}
        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydef})

        view = conf_obj.view("namespace")
        view["key"] = "bar"

        self.assertEqual(conf_obj["namespace.key"], "bar")

    def test_can_create_subview(self):
        keydef = {"namespace": {"subspace": {"key": {"_default": "foo"}}}}
        conf_obj = config.Configuration()
        conf_obj.attach_defs({"config": keydef})

        parentview = conf_obj.view("namespace")
        subview = parentview.view("subspace")

        self.assertEqual(subview["key"], parentview["subspace.key"])
        self.assertEqual(subview["key"], conf_obj["namespace.subspace.key"])
