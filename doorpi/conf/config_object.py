#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

class ConfigObject():

    __sections = {}

    def __init__(self, config):
        logger.debug("__init__")
        self.get_from_config(config)

    def __del__(self):
        logger.debug("__del__")

    def get(self, section, key, default = ''):
        logger.trace("get for key %s in section %s (default: %s)", key, section, default)
        return self.get_string(section, key, default)

    def get_string(self, section, key, default = ''):
        logger.trace("get_string for key %s in section %s (default: %s)", key, section, default)
        if section in self.__sections:
            if key in self.__sections[section]:
                if key is not 'password':
                    logger.trace("key '%s' exist in section '%s' with value '%s'", key, section, self.__sections[section][key])
                else:
                    logger.trace("key '%s' exist in section '%s' with value '%s'", key, section, '*******')
                return self.__sections[section][key]
            else:
                logger.trace("key '%s' doesn't exist in section '%s' ", key, section)
        else:
            logger.trace("section '%s' doesn't exist", section)

        logger.trace("return default")
        return default

    def get_int(self, section, key, default = -1):
        logger.trace("get_int for key %s in section %s (default: %s)", key, section, default)
        value = self.get_string(section, key)
        if value is not '': return int(value)
        else: return default

    def get_sections(self):
        logger.trace("get_sections")
        return_list = []
        for section in self.__sections:
            return_list.append(section)
        return return_list

    def get_keys(self, section):
        logger.trace("get_keys for section %s", section)
        return_list = []
        if section not in self.__sections: return []
        for key in self.__sections[section]:
            return_list.append(key)
        return return_list

    def get_from_config(self, config):
        logger.trace("get_from_config")
        for section in config.sections():
            self.__sections[section] = {}
            for key, value in config.items(section):
                if key.startswith(';') or key.startswith('#'): continue
                self.__sections[section][str(key)] = str(value)