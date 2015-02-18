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

    def get_string(self, section, key, default = '', log = True):
        value = ""
        if section in self.__sections:
            if key in self.__sections[section]:
                value = self.__sections[section][key]

        if key is 'password':
            if log: logger.trace("get_string for key %s in section %s (default: %s) returns %s", key, section, default, '*******')
        else:
            if log: logger.trace("get_string for key %s in section %s (default: %s) returns %s", key, section, default, value)
        return value

    def get_float(self, section, key, default = -1, log = True):
        value = self.get_string(section, key, log = False)
        if value is not '': value = float(value)
        else: value = default
        if log: logger.trace("get_integer for key %s in section %s (default: %s) returns %s", key, section, default, value)
        return value

    def get_integer(self, section, key, default = -1, log = True):
        value = self.get_string(section, key, log = False)
        if value is not '': value = int(value)
        else: value = default
        if log: logger.trace("get_integer for key %s in section %s (default: %s) returns %s", key, section, default, value)
        return value

    def get_boolean(self, section, key, default = False, log = True):
        value = self.get(section, key, str(default), log = False)
        value = value.lower() in ['true', 'yes', 'ja', '1']
        if log: logger.trace("get_boolean for key %s in section %s (default: %s) returns %s", key, section, default, value)
        return value

    def get_list(self, section, key, default = False, log = True):
        value = self.get(section, key, default, log = False)
        #TODO: value to list und Abfrage ob List leer - dann default
        return default

    def get_sections(self, filter = '', log = True):
        return_list = []
        for section in self.__sections:
            if filter in section: return_list.append(section)
        if log: logger.trace("get_sections returns %s", return_list)
        return return_list

    def get_keys(self, section, filter = '', log = True):
        return_list = []
        if section not in self.__sections:
            logging.warning("section %s not found in configfile", section)
        else:
            for key in self.__sections[section]:
                if filter in key: return_list.append(key)
        if log: logger.trace("get_keys for section %s returns %s", section, return_list)
        return return_list

    def get_from_config(self, config, log = True):
        if log: logger.trace("get_from_config")
        for section in config.sections():
            self.__sections[section] = {}
            for key, value in config.items(section):
                if key.startswith(';') or key.startswith('#'): continue
                self.__sections[section][str(key)] = str(value)

    get = get_string
    get_bool = get_boolean
    get_int = get_integer