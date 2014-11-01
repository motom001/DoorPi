#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import keyboard.base
import conf.config_object

import time # used by: DoorPi.run
import ConfigParser # used by: DoorPi.__init__
import os # used by: DoorPi.load_config

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class DoorPi(object):
    __metaclass__ = Singleton

    __config = None
    def get_config(self):
        return self.__config

    __keyboard = None
    def get_keyboard(self):
        return self.__keyboard

    __sipphone = None
    def get_sipphone(self):
        return self.__sipphone

    __current_call = None
    def get_current_call(self):
        return self.__current_call
    def set_current_call(self, call):
        if self.__current_call is not None:
            logger.warning("replace current_call while current_call is not None")
        self.__current_call = call
        return self.get_current_call()

    def __init__(self):
        logger.debug("__init__")

    def prepare(self, configfile = None):
        logger.debug("init")

        if not configfile and not self.__config:
            raise Exception("no config exists an no new given")

        self.__config = self.load_config(configfile)
        self.__keyboard = self.detect_keyboard()
        #self.__keyboard.self_test()
        self.__sipphone = self.detect_sipphone()
        self.__sipphone.start()
        return self

    def __del__(self):
        self.destroy()

    def destroy(self):
        logger.debug("destroy")
        if self.__keyboard is not None:
            self.__keyboard.destroy()
            self.__keyboard = None
            del self.__keyboard

        if self.__sipphone is not None:
            self.__sipphone.destroy()
            self.__sipphone = None
            del self.__sipphone

    def run(self):
        logger.debug("run")

        led = self.__config.get_int('DoorPi', 'is_alive_led')

        while True:
            current_pin = self.__keyboard.is_key_pressed()

            if current_pin is not None:
                logger.info("DoorPi.run: Key %s is pressed", str(current_pin))

                action = self.__config.get('InputPins', str(current_pin))
                logger.debug("start action: %s",action)

                if action.startswith('break'): break
                if action.startswith('call:'):
                    self.__current_call = self.__sipphone.make_call(action[len('call:'):])
                time.sleep(1) # for fat fingers

            if led is not '': self.is_alive_led(led)
            time.sleep(0.1)

        return self

    def is_alive_led(self, led):
        # blink, status led, blink
        if int(round(time.time())) % 2:
            self.__keyboard.set_output(
                pin = led,
                start_value = 1,
                end_value = 1,
                timeout = 0.0,
                log_output = False
            )
        else:
            self.__keyboard.set_output(
                pin = led,
                start_value = 0,
                end_value = 0,
                timeout = 0.0,
                log_output = False
            )

    def fire_action(self, action, secure_source = False):
        logger.debug("fire_action (%s)", action)

        if action.startswith('out:'):
            parameters = action[len('out:'):].split(',')
            return self.fire_action_out(
                pin = int(parameters[0]),
                start_value = int(parameters[1]),
                end_value = int(parameters[2]),
                timeout = int(parameters[3])
            )

        if action == 'reboot' and secure_source:
            logger.debug("system going down for reboot")
            # TODO: fill with content
            return False

        if action == 'restart' and secure_source:
            logger.debug("restart doorpi service")
            # TODO: fill with content
            return False

        logger.debug("couldn't find action or source was not set to secure")
        return False

    def fire_action_out(self, pin, start_value, end_value, timeout):
        self.__keyboard.set_output(
            pin = pin,
            start_value = start_value,
            end_value = end_value,
            timeout = timeout,
        )

    def load_config(self, configfile):
        logger.debug("load_config (%s)",configfile)
        logger.debug("use configfile: %s", configfile.name)
        config = ConfigParser.ConfigParser()
        config.read(configfile.name)
        if config.sections():
            logger.info("founded empty configfile - start write_demo_configfile")
            configfile.close()
            os.remove(configfile.name)
            config = self.write_demo_configfile(configfile.name)

        return conf.config_object.ConfigObject(config)

    def write_demo_configfile(self, config_filename):
        logger.debug("write_demo_configfile (%s)",config_filename)

        # http://stackoverflow.com/questions/8533797/adding-comment-with-configparser
        ConfigParser.ConfigParser.add_comment = lambda self, section, option, value: self.set(section, '; '+option, value)

        config = ConfigParser.ConfigParser()

        config.add_section('SIP-Phone')
        config.set('SIP-Phone', 'sipphonetyp', 'pjsua')
        config.set('SIP-Phone', 'server', '192.168.178.1')
        config.set('SIP-Phone', 'username', '621')
        config.set('SIP-Phone', 'password', 'raspberry')
        config.set('SIP-Phone', 'realm', 'fritz.box')
        config.set('SIP-Phone', 'dialtone', '/home/pi/DoorPi_1.0.3/doorpi/media/ShortDialTone.wav')

        config.add_section('DTMF')
        config.add_comment('DTMF', '"DTMF Signal"', 'out:[output_key],[start_value],[end_value],[timeout]')
        config.set('DTMF', '"#"', 'out:0,1,0,3')
        config.set('DTMF', '"**1"', 'restart')
        config.set('DTMF', '"**2"', 'reboot')

        config.add_section('InputPins')
        config.add_comment('InputPins','singlecall_pin','call:[phonenumber] # make a call to this number')
        config.set('InputPins', '0', 'call:5973922')
        config.add_comment('InputPins','multicall_pin','[call:[phonenumber], call:[phonenumber]] # make a call to all this numbers, first answer wins')
        config.set('InputPins', '1', 'call:01783558321')
        config.add_comment('InputPins','break_pin','break # break watching inputkeys and stop doorpi')
        config.set('InputPins', '3', 'break')

        config.add_section('OutputPins')
        config.set('OutputPins', '0', 'open_door 0')
        config.set('OutputPins', '1', 'switch_light 0')
        config.set('OutputPins', '7', 'is_alive_led')

        config.add_section('DoorPi')
        config.add_comment('DoorPi','is_alive_led','blink led for "system is still working"')
        config.set('DoorPi', 'is_alive_led', '7')

        config.add_section('AdminNumbers')
        config.set('AdminNumbers', '01783558321', 'active')
        config.set('AdminNumbers', '+491783558321', 'active')
        config.set('AdminNumbers', '5973922', 'active')
        config.set('AdminNumbers', '035295973922', 'active')
        config.set('AdminNumbers', '+4935295973922', 'active')

        #config.add_section('Log-File')
        #config.set('Log-File', 'Logfile', configfilename)
        #config.set('Log-File', 'Loglevel', 'DEBUG')

        with open(config_filename, 'wb') as configfile:
            config.write(configfile)
        return config

    def detect_sipphone(self):
        # find installed keyboards by import of libraries
        try:
            import pjsua
            import sipphone.by_pjsua
        except ImportError as exc:
            logger.info("Error: failed to import settings module ({})".format(exc))
            return None
        else:
            logger.debug("use keyboard 'PiFace'")
            return sipphone.by_pjsua.Pjsua()

    def detect_keyboard(self):
        # find installed keyboards by import of libraries
        try:
            import piface.pfio
            import keyboard.from_piface
        except ImportError as exc:
            logger.info("Error: failed to import settings module ({})".format(exc))
        else:
            logger.debug("use keyboard 'PiFace'")
            return keyboard.from_piface.PiFace(
                input_pins = self.__config.get_keys('InputPins'),
                output_pins = self.__config.get_keys('OutputPins')
            )

        try:
            import RPi.GPIO
            import keyboard.from_gpio
        except ImportError as exc:
            logger.info("Error: failed to import settings module ({})".format(exc))
            logger.critical("no GPIO availible - no keyboards found")
            return None
        else:
            logger.debug("use keyboard 'GPIO'")
            return keyboard.from_gpio.GPIO()

