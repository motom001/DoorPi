import logging
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path

import doorpi

LOGGER = logging.getLogger(__name__)


class ConfigObject:
    """The configuration manager for DoorPi."""

    def __init__(self, path):
        self.__path = Path(path).resolve()
        self.__config = ConfigParser(allow_no_value=True, strict=True,
                                     interpolation=ExtendedInterpolation())
        LOGGER.info("Loading configuration from %s", self.__path)
        try:
            with self.__path.open("r") as conffile:
                self.__config.read_file(conffile)
        except FileNotFoundError:
            self.save_config()

    def save_config(self):
        """Saves the configuration to disk."""
        try:
            self.__path.parent.mkdir(parents=True, exist_ok=True)
            with self.__path.open("w") as conffile:
                self.__config.write(conffile)
        except OSError as ex:
            LOGGER.error("Cannot write configuration file: %s", ex)

    def set_value(self, section, key, value):
        """Sets a key in a section to the given value."""
        if section == "DEFAULT":
            raise ValueError("Cannot set default values")
        if section not in self.__config:
            self.__config[section] = {}
        self.__config[section][key] = str(value)

    def delete_section(self, section):
        """Deletes an entire section from the configuration file."""
        del self.__config[section]

    def delete_key(self, section, key):
        """Deletes a key from the configuration."""
        del self.__config[section][key]

    def get_string_parsed(self, section, key, default=""):
        """Fetches a string and parses it."""
        return doorpi.INSTANCE.parse_string(self.get_string(section, key, default))

    def get_path(self, section, key, default=""):
        """Fetches a Path from the configuration."""
        val = self.get_string_parsed(section, key, default)
        if val: return Path(val)
        return None

    def get_string(self, section, key, default=""):
        """Fetches a string from the configuration."""
        try:
            return self.__config[section].get(key, default)
        except KeyError:
            return default

    def get_float(self, section, key, default=-1):
        """Fetches a floating point number from the configuration."""
        try:
            return self.__config[section].getfloat(key, default)
        except KeyError:
            return default
        except ValueError as err:
            LOGGER.error("Cannot read [%s].%s from config: %s", section, key, err)
            return default

    def get_int(self, section, key, default=-1):
        """Fetches an integer number from the configuration."""
        try:
            return self.__config[section].getint(key, default)
        except KeyError:
            return default
        except ValueError as err:
            LOGGER.error("Cannot read [%s].%s from config: %s", section, key, err)
            return default

    def get_bool(self, section, key, default=False):
        """Fetches a boolean value from the configuration."""
        try:
            return self.__config[section].getboolean(key, default)
        except KeyError:
            return default
        except ValueError as err:
            LOGGER.error("Cannot read [%s].%s from config: %s", section, key, err)
            return default

    def get_list(self, section, key, default=None, separator=","):
        """Fetches a list of multiple values from the configuration."""
        try:
            val = self.__config[section][key]
        except KeyError:
            return default or []
        return val.split(separator)

    def get_section(self, section):
        """Returns the copy of a configuration section as dict."""
        try:
            return dict(self.__config[section])
        except KeyError:
            return {}

    def get_sections(self, filter_=""):
        """Lists the configuration sections whose name contains ``filter_``."""
        return [s for s in self.__config.sections() if filter_ in s]

    def get_keys(self, section, filter_=""):
        """Lists the keys in the named section whose name contains ``filter_``."""
        try:
            return [s for s in self.__config[section] if filter_ in s]
        except KeyError:
            return []
