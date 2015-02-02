#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import sys
import argparse

import time # used by: DoorPi.run
import os # used by: DoorPi.load_config

#from math import abs

import datetime # used by: parse_string
import cgi # used by: parse_string
import threading
import BaseHTTPServer

import metadata
from keyboard.KeyboardInterface import load_keyboard
from sipphone.SipphoneInterface import load_sipphone
from conf.config_object import ConfigObject
from action.handler import EventHandler
from status.status_class import DoorPiStatus
from status.webservice import run_webservice, WebService
from action.base import SingleAction

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

    @property
    def base_path(self): return os.path.dirname(__file__)

    @property
    def epilog(self): return metadata.epilog

    __shutdown = False
    @property
    def shutdown(self): return self.__shutdown

    @property
    def base_path(self): return metadata.base_path

    def __init__(self, parsed_arguments = None):
        self.__parsed_arguments = parsed_arguments
        # for start as daemon - if start as app it will not matter to load this vars
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path =  '/var/run/doorpi.pid'
        self.pidfile_timeout = 5

        self.__last_tick = time.time()

    def prepare(self, parsed_arguments):
        logger.debug("prepare")
        logger.debug("givven arguments argv: %s", parsed_arguments)

        if not parsed_arguments.configfile and not self.config:
            raise Exception("no config exists an no new given")

        self.__event_handler = EventHandler()

        self.__config = ConfigObject.load_config(parsed_arguments.configfile)
        self.__keyboard = load_keyboard()
        logger.debug('Keyboard is now %s', self.keyboard.name)
        self.__sipphone = load_sipphone()
        self.sipphone.start()

        #register own events
        self.event_handler.register_event('OnStartup', __name__)
        self.event_handler.register_event('OnShutdown', __name__)

        # register eventbased actions from configfile
        for event_section in self.config.get_sections('EVENT_'):
            logger.info("founded EVENT_ section '%s' in configfile", event_section)
            event_name = event_section[len('EVENT_'):]
            for action in sorted(self.config.get_keys(event_section)):
                logger.info("register action '%s' for event '%s'", action, event_name)
                self.event_handler.register_action(event_name, self.config.get(event_section, action))

        # register actions for inputpins
        section_name = 'InputPins'
        for input_pin in sorted(self.config.get_keys(section_name)):
            self.event_handler.register_action('OnKeyPressed_'+input_pin, self.config.get(section_name, input_pin))

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

    def destroy(self):
        try:
            if self.__prepared is not True: return False
            logger.debug('destroy')
            self.__shutdown = True
            if self.event_handler is not None:
                self.event_handler.fire_event_synchron('OnShutdown', __name__)

            if self.keyboard is not None:
                self.keyboard.destroy()

            if self.sipphone is not None:
                self.sipphone.destroy()

            if self.event_handler is not None:
                timeout = 2
                if not self.event_handler.idle:
                    logger.warning('wait for event_handler with runnig theards %s', self.event_handler.threads[1:])
                while not self.event_handler.idle and timeout > 0:
                    logger.info('wait %s seconds for theards %s', timeout, self.event_handler.threads[1:])
                    time.sleep(0.5)
                    timeout -= 0.5

                if timeout <= 0:
                    logger.error("waiting for theards timed out - there are still theards: %s", self.event_handler.threads[1:])

            if self.event_handler is not None:
                self.event_handler.unregister_source(__name__, True)
                self.event_handler.destroy()
                self.__event_handler = None
                del self.__event_handler

            self.__keyboard = None
            del self.__keyboard

            self.__sipphone = None
            del self.__sipphone

        except Exception as ex:
            logger.exception(ex)


    def run(self):
        logger.debug("run")
        if not self.__prepared: self.prepare(self.__parsed_arguments)

        self.event_handler.register_event('OnTimeTick', __name__)
        #self.event_handler.register_action('OnTimeTick', 'sleep:0.1')
        self.event_handler.register_action('OnTimeTick', 'time_tick:!last_tick!')
        self.event_handler.fire_event_asynchron('OnTimeTick', __name__)

        self.event_handler.fire_event_synchron('OnStartup', __name__)

        logger.info('DoorPi started successfully')
        logger.info('BasePath is %s', self.base_path)

        while True:
            self.__last_tick = time.time()
            self.__event_handler.fire_event_synchron('OnTimeTick', __name__)
            time.sleep(0.4)

        return self

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

        for output_pin in self.config.get_keys('OutputPins', log = False):
            mapping_table[self.config.get('OutputPins', output_pin, log = False)] = output_pin

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