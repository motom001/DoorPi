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
        return self.get_string(section, key, default)

    def get_string(self, section, key, default = ''):
        logger.debug("get_string")
        if section in self.__sections:
            if key in self.__sections[section]:
                logger.debug("key '%s' exist in section '%s' with value '%s'", key, section, self.__sections[section][key])
                return self.__sections[section][key]
            else:
                logger.debug("key '%s' doesn't exist in section '%s' ", key, section)
        else:
            logger.debug("section '%s' doesn't exist", section)

        logger.debug("return default")
        return default

    def get_int(self, section, key, default = -1):
        value = self.get_string(section, key)
        if value is not '': return int(value)
        else: return default

    def get_sections(self):
        return_list = []
        for section in self.__sections:
            return_list.append(section)
        return return_list

    def get_keys(self, section):
        return_list = []
        if not self.__sections[section]: return []
        for key in self.__sections[section]:
            return_list.append(key)
        return return_list

    def get_from_config(self, config):
        for section in config.sections():
            self.__sections[section] = {}
            for key, value in config.items(section):
                if key.startswith(';') or key.startswith('#'): continue
                self.__sections[section][str(key)] = str(value)