# -*- coding: utf-8 -*-

import json
import importlib

from main import DOORPI

logger = DOORPI.register_module(__name__, return_new_logger=True)

from resources.functions.json import get_by_json_path


class ConfigHandler:
    _config_object = {}

    @property
    def json_pretty_printing(self):
        return json.dumps(self._config_object, sort_keys=True, indent=4, separators=(',', ': '))

    @staticmethod
    def dump_object(raw_object):
        return json.dumps(raw_object, sort_keys=True, indent=4, separators=(',', ': '))

    def __init__(self):
        pass

    def start(self):
        logger.info("start ConfigHandler with configfile %s", DOORPI.arguments.config_file)
        DOORPI.register_module(__name__, self.start, self.stop)
        self._config_object = self.load_config_from_configfile(DOORPI.arguments.config_file)
        return self

    def stop(self):
        logger.info("stop ConfigHandler")

    @staticmethod
    def load_config_from_configfile(config_file):
        with open(DOORPI.parse_string(config_file)) as data_file:
            config_object = json.load(data_file)
        return config_object

    @staticmethod
    def get_module_documentation_by_module_name(module_name):
        """
        Load module documentation for given module name.
        :param module_name: name of module
        :return: dict in form of documentation dict or empty dict if not found
        """
        try:
            return importlib.import_module(module_name + '.docs').DOCUMENTATION
        except:
            logger.warning('no docs founded for %s', module_name)
            return None

    def get_by_path(self, json_path, default=None, config_object=None, function='value'):
        # TODO: hole aus Docu den Parameter und nutze default und type für bessere Kontrolle
        # dict( json_path = 'resources/event_handler/event_log/typ', type = 'string', default = 'sqllite', mandatory = False, description = 'Typ der Event_Handler Datenbank (aktuell nur sqllite)')
        # if default: logger.warning('default given as parameter for %s', json_path)
        use_default = False
        try:
            if not config_object: config_object = self._config_object
            value = get_by_json_path(config_object, json_path)
        except Exception as exp:
            # logger.debug('failed to get %s with error %s', json_path, exp)
            value = default
            use_default = True

        try:
            if function == 'value':
                pass
            elif function == 'keys':
                value = value.keys()
            elif function == 'len':
                value = len(value)
            elif function == 'length':
                value = len(value)
        except Exception as exp:
            logger.error('failed to prepare value with function %s with error %s', function, exp)

        if value == default and use_default:
            log_message = "%s of %s: %s (use default)"
        elif value == default:
            log_message = "%s of %s: %s (was default)"
        else:
            log_message = "%s of %s: %s"

        if json_path.split('.')[-1] in DOORPI.CONST.CONFIG_PASSWORD_KEYS:
            logger.debug(log_message, function, json_path, '*********')
        else:
            logger.debug(log_message, function, json_path, str(value))
        return value

    def get_config_from_documentation_object(self, documentation_object):
        logger.debug('start get_config_from_documentation_object')
        return_array = documentation_object['configuration'] if 'configuration' in documentation_object else []
        for library_name in get_by_json_path(documentation_object, 'libraries', dict()):
            return_array += get_by_json_path(documentation_object['libraries'][library_name], 'configuration', [])
        return return_array

    def get_modul_config(self, module_name, config_object=None, module_documentation=None):
        if not self._config_object: return {}
        if not config_object: config_object = self._config_object
        if not module_documentation: module_documentation = importlib.import_module(module_name + '.docs').DOCUMENTATION
        all_config_keys = self.get_config_from_documentation_object(module_documentation)
        all_config_key_value = self.prepare_module_config(all_config_keys, config_object)
        return all_config_key_value

    def prepare_module_config(self, array_of_config_parameters, config_object):
        return_dict = dict()
        for config_parameter in array_of_config_parameters:
            name = config_parameter['json_path'].split('/').pop()
            value = get_by_json_path(config_object, config_parameter['json_path'])
            # type_name = get_by_json_path(config_object, config_parameter['type'], 'str')
            # if not str(type(value)) ==  type_name:
            #    logger.warning('%s should be %s but is %s', config_parameter['json_path'], type_name, str(type(value)))
            return_dict[name] = value
        return return_dict

    __call__ = get_by_path
