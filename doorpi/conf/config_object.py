import logging
from configparser import ConfigParser, ExtendedInterpolation
from pathlib import Path

import doorpi


logger = logging.getLogger(__name__)


class ConfigObject:

    def __init__(self, path):
        self.__path = Path(path).resolve()
        self.__config = ConfigParser(allow_no_value=True, strict=True,
                                     interpolation=ExtendedInterpolation())
        logger.info("Loading configuration from %s", self.__path)
        try:
            with self.__path.open("r") as f:
                self.__config.read_file(f)
        except FileNotFoundError: self.save_config()
        except Exception as ex:
            logger.error("Cannot load configuration from %s: %s", self.__path, ex)

    def save_config(self):
        try:
            self.__path.parent.mkdir(parents=True, exist_ok=True)
            with self.__path.open("w") as f:
                self.__config.write(f)
        except Exception as ex:
            logger.error("Cannot write configuration file: %s", ex)

    def set_value(self, section, key, value):
        if section == "DEFAULT":
            raise ValueError("Cannot set default values")
        if section not in self.__config:
            self.__config[section] = {}
        self.__config[section][key] = str(value)

    def delete_section(self, section, *, delete_empty_only=True):
        del self.__config[section]

    def get_string_parsed(self, section, key, default=""):
        return doorpi.DoorPi().parse_string(self.get_string(section, key, default))

    def get_path(self, section, key, default=""):
        val = self.get_string_parsed(section, key, default)
        if val: return Path(val)
        else: return None

    def get_string(self, section, key, default=""):
        try: return self.__config[section].get(key, default)
        except KeyError: return default

    def get_float(self, section, key, default=-1):
        try: return self.__config[section].getfloat(key, default)
        except KeyError: return default
        except ValueError as err:
            logger.error("Cannot read [%s].%s from config: %s", section, key, err)
            return default

    def get_int(self, section, key, default=-1):
        try: return self.__config[section].getint(key, default)
        except KeyError: return default
        except ValueError as err:
            logger.error("Cannot read [%s].%s from config: %s", section, key, err)
            return default

    def get_bool(self, section, key, default=False):
        try: return self.__config[section].getboolean(key, default)
        except KeyError: return default
        except ValueError as err:
            logger.error("Cannot read [%s].%s from config: %s", section, key, err)
            return default

    def get_list(self, section, key, default=[], separator=","):
        try: val = self.__config[section].get(key, separator.join(default))
        except KeyError: val = default
        if val == "": return []
        else: return val.split(separator)

    def get_section(self, section):
        try: return dict(self.__config[section])
        except KeyError: return {}

    def get_sections(self, filter=""):
        return [s for s in self.__config.sections() if filter in s]

    def get_keys(self, section, filter=""):
        try: return [s for s in self.__config[section] if filter in s]
        except KeyError: return []
