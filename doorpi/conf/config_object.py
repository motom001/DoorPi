#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import os

import ConfigParser
import doorpi

from backward_compatibility import BACKWARD_COMPATIBILITY_KEYS

class ConfigObject():

    __sections = {}
    _config_file = None

    @property
    def all(self): return self.__sections

    @property
    def config_file(self): return self._config_file

    def __init__(self, config, config_file = None):
        logger.debug("__init__")
        self.get_from_config(config)
        self._config_file = config_file

    def __del__(self):
        return self.destroy()

    def destroy(self):
        logger.debug("__del__")
        #DoorPi().event_handler.unregister_source(__name__, True)
        return True

    @staticmethod
    def find_config(configfile = None):
        try:
            open(configfile.name, 'r').close()
            return configfile.name
        except AttributeError: pass
        except IOError: pass

        default_files = [
            str(configfile),
            doorpi.DoorPi().parse_string(str(configfile)),
            os.path.join('!BASEPATH!', 'conf', 'doorpi.ini'),
            os.path.join('!BASEPATH!', 'conf', 'doorpi.cfg')
        ]

        for possible_default_file in default_files:
            try:
                possible_default_file = doorpi.DoorPi().parse_string(possible_default_file)
                open(possible_default_file, 'r').close()
                return possible_default_file
            except: pass

        return None

    @staticmethod
    def load_config(configfile, search_for_defaults = True):
        config = ConfigParser.ConfigParser(allow_no_value = True)
        if search_for_defaults: configfile_name = ConfigObject.find_config(configfile)
        else: configfile_name = configfile

        if not configfile_name:
            logger.error('No valid configfile found - use parameter --configfile "filename" to specify one')
            return ConfigObject(config)

        logger.info("use configfile: %s", configfile_name)

        config.read(configfile_name)
        return ConfigObject(config, configfile_name)

    def save_config(self, configfile = ''):
        if not configfile: configfile = self.config_file
        if not configfile: configfile = self.find_config(configfile)
        if not configfile: configfile = doorpi.DoorPi().parse_string(os.path.join('!BASEPATH!', 'conf', 'doorpi.ini'))

        #if not configfile: return False
        logger.debug("write configfile: %s", configfile)
        try:
            if not os.path.exists(os.path.dirname(configfile)):
                logger.info('Path %s does not exist - creating it now', os.path.dirname(configfile))
                os.makedirs(os.path.dirname(configfile))
            cfgfile = open(configfile,'w')
            config = ConfigParser.ConfigParser(allow_no_value = True)
            for section in sorted(self.__sections.keys()):
                config.add_section(section)
                for key in sorted(self.__sections[section].keys()):
                    config.set(section, key, self.__sections[section][key])
            config.write(cfgfile)
            cfgfile.close()
            logger.info("write configfile was success: %s", configfile)
            return True
        except Exception as exp:
            logger.exception(exp)
            return False

    def get_string_parsed(self, section, key, default = '', log = True):
        raw_string = self.get_string(section, key, default, log)
        parsed_string = doorpi.DoorPi().parse_string(raw_string)
        logger.debug('parse string "%s" to "%s"', raw_string, parsed_string)
        return parsed_string

    def set_value(self, section, key, value, log = True, password = False):
        if section not in self.__sections.keys():
            self.__sections[section] = {}

        password_friendly_value = "*******" if key is 'password' or password else value

        if key not in self.__sections[section].keys():
            if log: logger.debug("create new key %s in section %s with value '%s'",
                                 key, section, password_friendly_value)
        else:
            if log: logger.debug("overwrite key %s in section %s from '%s' to '%s'",
                                 key, section, self.__sections[section][key], password_friendly_value)

        self.__sections[section][key] = value
        return True

    def rename_key(self, section, old_key, new_key, default = '', log = True):
        if log: logging.debug('rename key from %s to %s in section %s', old_key, new_key, section)
        old_value = self.get_string(section, old_key, default, log, store_if_not_exists = False)
        self.set_value(
            section = section,
            key = new_key,
            value = old_value,
            log = log
        )
        self.delete_key(section, old_key, log = log)

    def delete_section(self, section, delete_empty_only = True, log = True):
        if section in self.__sections and len(self.__sections[section]) > 0 and delete_empty_only:
            logger.warning("could not delete section %s, because it's not empty.", section)
            return False

        try:
            if len(self.__sections[section]) > 0 and delete_empty_only:
                raise KeyError('section is not empty')

            self.__sections.pop(section)
            return True
        except KeyError as exp:
            if log: logger.warning('delete section %s failed: %s', section, exp)
            return False

    def delete_key(self, section, key, log = True):
        try:
            if log: logger.info('delete key %s from section %s', key, section)
            self.__sections[section].pop(key)
            self.delete_section(section, log = log)

            return True
        except KeyError as exp:
            if log: logger.warning('delete key %s from section %s failed: %s', key, section, exp)
        return False

    def get_string(self, section, key, default = '', log = True, password = False, store_if_not_exists = True):
        value = None
        try:
            old_section, old_key = BACKWARD_COMPATIBILITY_KEYS[section][key]
            value = self.__sections[old_section][old_key]
            self.delete_key(old_section, old_key, False)
            self.__sections[section][key] = value
            logger.warning('found %s - %s in BACKWARD_COMPATIBILITY_KEYS with %s - %s', section, key, old_section, old_key)
        except KeyError:
            try:
                value = self.__sections[section][key]
            except KeyError:
                pass
        
        if value is None:
            #logger.trace('no value found - use default')
            value = default
            if store_if_not_exists: self.set_value(section, key, default, log, password)

        if key.endswith('password') or password:
            if log: logger.trace("get_string for key %s in section %s (default: %s) returns %s", key, section, default, '*******')
        else:
            if log: logger.trace("get_string for key %s in section %s (default: %s) returns %s", key, section, default, value)
        return value

    def get_float(self, section, key, default = -1, log = True, store_if_not_exists = True):
        value = self.get_string(section, key, str(default), log = False, store_if_not_exists = store_if_not_exists)
        if value is not '': value = float(value)
        else: value = default
        if log: logger.trace("get_integer for key %s in section %s (default: %s) returns %s", key, section, default, value)
        return value

    def get_integer(self, section, key, default = -1, log = True, store_if_not_exists = True):
        value = self.get(section, key, str(default), log = False, store_if_not_exists = store_if_not_exists)
        if value is not '': value = int(value)
        else: value = default
        if log: logger.trace("get_integer for key %s in section %s (default: %s) returns %s", key, section, default, value)
        return value

    def get_boolean(self, section, key, default = False, log = True, store_if_not_exists = True):
        value = self.get(section, key, str(default), log = False, store_if_not_exists = store_if_not_exists)
        value = value.lower() in ['true', 'yes', 'ja', '1']
        if log: logger.trace("get_boolean for key %s in section %s (default: %s) returns %s", key, section, default, value)
        return value

    def get_list(self, section, key, default = [], separator = ',', log = True, store_if_not_exists = True):
        value = self.get(section, key, str(default), log = False, store_if_not_exists = store_if_not_exists)
        if value is not '': value = value.split(separator)
        else: value = default
        if log: logger.trace("get_list for key %s in section %s (default: %s) returns %s", key, section, default, value)
        return value

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
