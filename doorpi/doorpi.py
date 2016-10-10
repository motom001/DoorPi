#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import sys
import argparse

import time  # used by: DoorPi.run
import os  # used by: DoorPi.load_config

import datetime  # used by: parse_string
import cgi  # used by: parse_string
import tempfile

import metadata
from keyboard.KeyboardInterface import load_keyboard
from sipphone.SipphoneInterface import load_sipphone
from status.webserver import load_webserver
from conf.config_object import ConfigObject
from action.handler import EventHandler
from status.status_class import DoorPiStatus
#from status.webservice import run_webservice, WebService
from action.base import SingleAction


class DoorPiShutdownAction(SingleAction): pass
class DoorPiNotExistsException(Exception): pass
class DoorPiEventHandlerNotExistsException(Exception): pass
class DoorPiRestartException(Exception): pass

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class DoorPi(object):
    __metaclass__ = Singleton

    __prepared = False

    __config = None
    @property
    def config(self): return self.__config

    __keyboard = None
    @property
    def keyboard(self): return self.__keyboard
    #def get_keyboard(self): return self.__keyboard

    __sipphone = None
    @property
    def sipphone(self): return self.__sipphone

    @property
    def additional_informations(self):
        if self.event_handler is None: return {}
        else: return self.event_handler.additional_informations

    __event_handler = None
    @property
    def event_handler(self): return self.__event_handler

    __webserver = None
    @property
    def webserver(self): return self.__webserver

    @property
    def status(self): return DoorPiStatus(self)
    def get_status(self, modules = '', value= '', name = ''): return DoorPiStatus(self, modules, value, name)

    @property
    def epilog(self): return metadata.epilog

    @property
    def name(self): return str(metadata.package)
    @property
    def name_and_version(self): return str(metadata.package) + " - version: " + metadata.version

    __shutdown = False
    @property
    def shutdown(self): return self.__shutdown

    _base_path = metadata.doorpi_path
    @property
    def base_path(self):
        if self._base_path is None:
            try:
                self._base_path = os.path.join(os.path.expanduser('~'), metadata.package)
                assert os.access(self._base_path, os.W_OK), 'use fallback for base_path (see tmp path)'
            except Exception as exp:
                logger.error(exp)
                import tempfile
                self._base_path = tempfile.gettempdir()
        return self._base_path

    def __init__(self, parsed_arguments = None):
        self.__parsed_arguments = parsed_arguments
        # for start as daemon - if start as app it will not matter to load this vars
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path =  '/var/run/doorpi.pid'
        self.pidfile_timeout = 5

        self.__last_tick = time.time()

    def doorpi_shutdown(self, time_until_shutdown=10):
        time.sleep(time_until_shutdown)
        self.__shutdown = True

    def prepare(self, parsed_arguments):
        logger.debug("prepare")
        logger.debug("given arguments argv: %s", parsed_arguments)

        self.__config = ConfigObject.load_config(parsed_arguments.configfile)
        self._base_path = self.config.get('DoorPi', 'base_path', self.base_path)
        self.__event_handler = EventHandler()

        if self.config.config_file is None:
            self.event_handler.register_action('AfterStartup', self.config.save_config)
            self.config.get('EVENT_OnStartup', '10', 'sleep:1')

        if 'test' in parsed_arguments and parsed_arguments.test is True:
            logger.warning('using only test-mode and destroy after 5 seconds')
            self.event_handler.register_action('AfterStartup', DoorPiShutdownAction(self.doorpi_shutdown))

        # register own events
        self.event_handler.register_event('BeforeStartup', __name__)
        self.event_handler.register_event('OnStartup', __name__)
        self.event_handler.register_event('AfterStartup', __name__)
        self.event_handler.register_event('BeforeShutdown', __name__)
        self.event_handler.register_event('OnShutdown', __name__)
        self.event_handler.register_event('AfterShutdown', __name__)
        self.event_handler.register_event('OnTimeTick', __name__)
        self.event_handler.register_event('OnTimeTickRealtime', __name__)

        # register base actions
        self.event_handler.register_action('OnTimeTick', 'time_tick:!last_tick!')

        # register modules
        self.__webserver    = load_webserver()
        self.__keyboard     = load_keyboard()
        self.__sipphone     = load_sipphone()
        self.sipphone.start()

        # register eventbased actions from configfile
        for event_section in self.config.get_sections('EVENT_'):
            logger.info("found EVENT_ section '%s' in configfile", event_section)
            event_name = event_section[len('EVENT_'):]
            for action in sorted(self.config.get_keys(event_section)):
                logger.info("registering action '%s' for event '%s'", action, event_name)
                self.event_handler.register_action(event_name, self.config.get(event_section, action))

        # register actions for inputpins
        if 'KeyboardHandler' not in self.keyboard.name:
            section_name = 'InputPins'
            for input_pin in sorted(self.config.get_keys(section_name)):
                self.event_handler.register_action('OnKeyPressed_'+input_pin, self.config.get(section_name, input_pin))
        else:
            for keyboard_name in self.keyboard.loaded_keyboards:
                section_name = keyboard_name+'_InputPins'
                for input_pin in self.config.get_keys(section_name, log = False):
                    self.event_handler.register_action(
                        'OnKeyPressed_'+keyboard_name+'.'+input_pin,
                        self.config.get(section_name, input_pin)
                    )

        # register actions for DTMF
        section_name = 'DTMF'
        for DTMF in sorted(self.config.get_keys(section_name)):
            self.event_handler.register_action('OnDTMF_'+DTMF, self.config.get(section_name, DTMF))

        # register keep_alive_led
        is_alive_led = self.config.get('DoorPi', 'is_alive_led', '')
        if is_alive_led is not '':
            self.event_handler.register_action('OnTimeSecondEvenNumber', 'out:%s,HIGH,False'%is_alive_led)
            self.event_handler.register_action('OnTimeSecondUnevenNumber', 'out:%s,LOW,False'%is_alive_led)

        self.__prepared = True
        return self

    def __del__(self):
        return self.destroy()

    @property
    def modules_destroyed(self):
        if len(self.event_handler.sources) > 1: return False
        return self.event_handler.idle

    def destroy(self):
        logger.debug('destroy doorpi')

        if not self.event_handler or self.event_handler.threads == None:
            DoorPiEventHandlerNotExistsException("don't try to stop, when not prepared")
            return False

        logger.debug("Threads before starting shutdown: %s", self.event_handler.threads)

        self.event_handler.fire_event('BeforeShutdown', __name__)
        self.event_handler.fire_event_synchron('OnShutdown', __name__)
        self.event_handler.fire_event('AfterShutdown', __name__)

        timeout = 5
        waiting_between_checks = 0.5
        time.sleep(waiting_between_checks)
        while timeout > 0 and self.modules_destroyed is not True:
            # while not self.event_handler.idle and timeout > 0 and len(self.event_handler.sources) > 1:
            logger.debug('wait %s seconds for threads %s and %s event',
                         timeout, len(self.event_handler.threads[1:]), len(self.event_handler.sources))
            logger.trace('still existing threads:       %s', self.event_handler.threads[1:])
            logger.trace('still existing event sources: %s', self.event_handler.sources)
            time.sleep(waiting_between_checks)
            timeout -= waiting_between_checks

        if timeout <= 0:
            logger.warning("waiting for threads to time out - there are still threads: %s", self.event_handler.threads[1:])

        logger.info('======== DoorPi successfully shutdown ========')
        return True

    def restart(self):
        if self.destroy(): self.run()
        else: raise DoorPiRestartException()

    def run(self):
        logger.debug("run")
        if not self.__prepared: self.prepare(self.__parsed_arguments)

        self.event_handler.fire_event('BeforeStartup', __name__)
        self.event_handler.fire_event_synchron('OnStartup', __name__)
        self.event_handler.fire_event('AfterStartup', __name__)

        # self.event_handler.register_action('OnTimeMinuteUnevenNumber', 'doorpi_restart')

        logger.info('DoorPi started successfully')
        logger.info('BasePath is %s', self.base_path)
        if self.__webserver:
            logger.info('Weburl is %s', self.__webserver.own_url)
        else:
            logger.info('no Webserver loaded')

        time_ticks = 0

        while True and not self.__shutdown:
            time_ticks += 0.05
            self.check_time_critical_threads()
            if time_ticks > 0.5:
                self.__last_tick = time.time()
                self.__event_handler.fire_event_asynchron('OnTimeTick', __name__)
                time_ticks = 0
            time.sleep(0.05)
        return self

    def check_time_critical_threads(self):
        if self.sipphone: self.sipphone.self_check()

    def parse_string(self, input_string):
        parsed_string = datetime.datetime.now().strftime(str(input_string))

        if self.keyboard is None or self.keyboard.last_key is None:
            self.additional_informations['LastKey'] = "NotSetYet"
        else:
            self.additional_informations['LastKey'] = str(self.keyboard.last_key)

        infos_as_html = '<table>'
        for key in self.additional_informations.keys():
            infos_as_html += '<tr><td>'
            infos_as_html += '<b>'+key+'</b>'
            infos_as_html += '</td><td>'
            infos_as_html += '<i>'+cgi.escape(
                str(self.additional_informations.get(key)).replace("\r\n", "<br />")
            )+'</i>'
            infos_as_html += '</td></tr>'
        infos_as_html += '</table>'

        mapping_table = {
            'INFOS_PLAIN':      str(self.additional_informations),
            'INFOS':            infos_as_html,
            'BASEPATH':         self.base_path,
            'last_tick':        str(self.__last_tick)
        }

        for key in metadata.__dict__.keys():
            if isinstance(metadata.__dict__[key], str):
                mapping_table[key.upper()] = metadata.__dict__[key]

        if self.config:
            mapping_table.update({
                'LAST_SNAPSHOT':    str(self.config.get_string('DoorPi', 'last_snapshot', log=False))
            })
        if self.keyboard and 'KeyboardHandler' not in self.keyboard.name:
            for output_pin in self.config.get_keys('OutputPins', log = False):
                mapping_table[self.config.get('OutputPins', output_pin, log = False)] = output_pin
        elif self.keyboard and 'KeyboardHandler' in self.keyboard.name:
            for outputpin_section in self.config.get_sections('_OutputPins', False):
                for output_pin in self.config.get_keys(outputpin_section, log = False):
                    mapping_table[self.config.get(outputpin_section, output_pin, log = False)] = output_pin

        for key in mapping_table.keys():
            parsed_string = parsed_string.replace(
                "!"+key+"!",
                mapping_table[key]
            )

        for key in self.additional_informations.keys():
            parsed_string = parsed_string.replace(
                "!"+key+"!",
                str(self.additional_informations[key])
            )

        return parsed_string

if __name__ == '__main__':
    raise Exception('use main.py to start DoorPi')