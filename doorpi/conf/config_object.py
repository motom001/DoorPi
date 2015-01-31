#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import ConfigParser

class ConfigObject():

    __sections = {}
    @property
    def all(self): return self.__sections

    def __init__(self, config):
        logger.debug("__init__")
        self.get_from_config(config)

    def __del__(self):
        return self.destroy()

    def destroy(self):
        logger.debug("__del__")
        #DoorPi().event_handler.unregister_source(__name__, True)
        return True

    @staticmethod
    def load_config(configfile):
        logger.debug("load_config (%s)",configfile)
        logger.debug("use configfile: %s", configfile.name)
        config = ConfigParser.ConfigParser()
        config.read(configfile.name)
        if not config.sections():
            configfile.close()
            raise Exception("No valid configfile found at "+configfile)
        return ConfigObject(config)

    def get_string(self, section, key, default = ''):
        logger.trace("get_string for key %s in section %s (default: %s)", key, section, default)
        if section in self.__sections:
            if key in self.__sections[section]:
                if key is 'password':
                    logger.trace("key '%s' exist in section '%s' with value '%s'", key, section, '*******')
                else:
                    logger.trace("key '%s' exist in section '%s' with value '%s'", key, section, self.__sections[section][key])
                return self.__sections[section][key]
            else:
                logger.trace("key '%s' doesn't exist in section '%s' ", key, section)
        else:
            logger.trace("section '%s' doesn't exist", section)

        logger.trace("return default '%s", default)
        return default

    def get_float(self, section, key, default = -1):
        logger.trace("get_float for key %s in section %s (default: %s)", key, section, default)
        value = self.get_string(section, key)
        if value is not '': return float(value)
        else: return default

    def get_integer(self, section, key, default = -1):
        logger.trace("get_integer for key %s in section %s (default: %s)", key, section, default)
        value = self.get_string(section, key)
        if value is not '': return int(value)
        else: return default

    def get_boolean(self, section, key, default = False):
        value = self.get(section, key, str(default))
        return value.lower() in ['true', 'yes', 'ja', '1']

    def get_list(self, section, key, default = False):
        value = self.get(section, key, default)
        #TODO: value to list und Abfrage ob List leer - dann default
        return default

    def get_sections(self, filter = ''):
        logger.trace("get_sections")
        return_list = []
        for section in self.__sections:
            if filter in section: return_list.append(section)
        return return_list

    def get_keys(self, section, filter = ''):
        logger.trace("get_keys for section %s", section)
        return_list = []
        if section not in self.__sections: return []
        for key in self.__sections[section]:
            if filter in key: return_list.append(key)
        return return_list

    def get_from_config(self, config):
        logger.trace("get_from_config")
        for section in config.sections():
            self.__sections[section] = {}
            for key, value in config.items(section):
                if key.startswith(';') or key.startswith('#'): continue
                self.__sections[section][str(key)] = str(value)

    get = get_string
    get_bool = get_boolean
    get_int = get_integer