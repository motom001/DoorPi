#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import sys
import argparse

from keyboard.KeyboardInterface import detect_keyboard
import conf.config_object

import time # used by: DoorPi.run
import ConfigParser # used by: DoorPi.__init__
import os # used by: DoorPi.load_config
import smtplib # used by: fire_action_mail
from email.mime.multipart import MIMEMultipart # used by: fire_action_mail
from email.mime.text import MIMEText # used by: fire_action_mail
from email.Utils import COMMASPACE # used by: fire_action_mail
import datetime # used by: parse_string
import cgi # used by: parse_string

import metadata

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class DoorPi(object):
    __metaclass__ = Singleton

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

    __additional_informations = {}
    @property
    def additional_informations(self): return self.__additional_informations

    def __init__(self):
        logger.debug("__init__")
        # for start as daemon - if start as app it will not matter to load this vars
        self.stdin_path = '/dev/null'
        self.stdout_path = '/var/log/doorpi/stdout.log'
        self.stderr_path = '/var/log/doorpi/stderr.log'
        self.pidfile_path =  '/var/run/doorpi.pid'
        self.pidfile_timeout = 5

    def prepare(self):
        logger.debug("prepare")

        parsed_arguments = self.parse_argv()
        logger.debug("givven arguments argv: %s", parsed_arguments)

        if not parsed_arguments.configfile and not self.config:
            raise Exception("no config exists an no new given")

        self.__config = self.load_config(parsed_arguments.configfile)
        self.__keyboard = detect_keyboard()
        logger.debug('Keyboard is now %s', self.keyboard.name)
        self.__sipphone = self.detect_sipphone()
        self.sipphone.start()
        return self

    def parse_argv(self):
        logger.debug('parse_argv')

        arg_parser = argparse.ArgumentParser(
            prog=sys.argv[0],
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=metadata.description,
            epilog = metadata.epilog)

        arg_parser.add_argument(
            '-V', '--version',
            action='version',
            version='{0} {1}'.format(metadata.project, metadata.version))

        arg_parser.add_argument(
            '--configfile',
            help='configfile for DoorPi',
            type=file,
            dest='configfile',
            required = True)

        if  len(sys.argv) > 1 and sys.argv[1] in ['start', 'stop', 'restart', 'status']: # running as daemon? cut first argument
            return  arg_parser.parse_args(args=sys.argv[2:])
        else:
            return  arg_parser.parse_args(args=sys.argv[1:])

    def __del__(self):
        self.destroy()

    def destroy(self):
        logger.debug("destroy")
        self.fire_event('OnShutdown')

        if self.keyboard is not None:
            self.keyboard.destroy()
            self.__keyboard = None
            del self.__keyboard

        if self.sipphone is not None:
            self.sipphone.destroy()
            self.__sipphone = None
            del self.__sipphone

    def run(self):
        logger.debug("run")

        self.prepare()

        led = self.config.get_int('DoorPi', 'is_alive_led')

        self.fire_event('OnStartup')

        logger.info('DoorPi started successfully')

        while True:
            current_pin = self.keyboard.pressed_key
            if current_pin is not None:
                self.fire_event('BeforeKeyPressed')
                logger.info("DoorPi.run: Key %s is pressed", str(current_pin))

                action = self.config.get('InputPins', str(current_pin))
                logger.debug("start action: %s",action)

                if action.startswith('break'): break

                self.fire_action(action, True)

                self.fire_event('AfterKeyPressed')

            if led is not '': self.is_alive_led(led)

        return self

    def is_alive_led(self, led):
        # blink, status led, blink
        if int(round(time.time())) % 2:
            self.keyboard.set_output(
                pin = led,
                start_value = 1,
                end_value = 1,
                timeout = 0.0,
                log_output = False
            )
        else:
            self.keyboard.set_output(
                pin = led,
                start_value = 0,
                end_value = 0,
                timeout = 0.0,
                log_output = False
            )

    def fire_event(self, event_name, additional_informations = {}, secure_source = True):
        logger.trace('get event(event_name = %s, additional_informations = %s, secure_source = %s)', event_name, additional_informations, secure_source)
        self.__additional_informations = additional_informations
        if self.config is not None:
            for action in sorted(self.config.get_keys(event_name)):
                logger.trace("fire action %s for event %s", action, event_name)
                self.fire_action(self.config.get(event_name, action), secure_source)
        self.__additional_informations = {}
        return True

    def fire_action(self, action, secure_source = False):
        logger.debug("fire_action (%s) and secure_source is %s", action, secure_source)

        if action.startswith('recheck:'):
            parameters = action[len('out:'):].split(',')
            return self.fire_action_recheck()

        if action.startswith('event:'):
            return self.fire_event(action[len('event:'):])

        if action.startswith('call:'):
            return self.sipphone.make_call(action[len('call:'):])

        if action.startswith('out:'):
            parameters = action[len('out:'):].split(',')
            if len(parameters) == 4:
                return self.fire_action_out(
                    pin = int(parameters[0]),
                    start_value = int(parameters[1]),
                    end_value = int(parameters[2]),
                    timeout = int(parameters[3])
                )
            elif len(parameters) == 5:
                return self.fire_action_out(
                    pin = int(parameters[0]),
                    start_value = int(parameters[1]),
                    end_value = int(parameters[2]),
                    timeout = int(parameters[3]),
                    stop_pin = int(parameters[4])
                )
            else:
                logger.error('worng parameterlength for action %s', action)
                return True

        if action.startswith('mailto:'):
            parameters = action[len('mailto:'):].split(',')
            return self.fire_action_mail(
                smtp_to = parameters[0],
                smtp_subject = parameters[1],
                smtp_text = parameters[2]
            )

        if action == 'reboot' and secure_source:
            logger.debug("system going down for reboot")
            system.os('sudo /etc/init.d/doorpi restart')
            return True

        if action == 'restart' and secure_source:
            logger.debug("restart doorpi service")
            system.os('sudo reboot')
            return True

        if action.startswith('sleep:'):
            try:
                time.sleep(float(action[len('sleep:'):]))
                return True
            except:
                logger.exception('exception while action "sleep"')
                return False

        logger.debug("couldn't find action or source was not set to secure")
        return False

    def fire_action_watch(self, input_pin, total_time, interval = 0.5):
        return True

    def fire_action_out(self, pin, start_value, end_value, timeout, stop_pin = None):
        if self.keyboard is None:
            logger.warning("couldn't fire_action_out - no keyboard present")
            return
        return self.keyboard.set_output(
            pin = pin,
            start_value = start_value,
            end_value = end_value,
            timeout = timeout,
            stop_pin = stop_pin
        )

    def fire_action_mail(self, smtp_to, smtp_subject, smtp_text):
        try:
            smtp_host = self.config.get('SMTP', 'server')
            smtp_port = self.config.get_int('SMTP', 'port')
            smtp_user = self.config.get('SMTP', 'username')
            smtp_password = self.config.get('SMTP', 'password')
            smtp_from = self.config.get('SMTP', 'from')

            smtp_tolist = smtp_to.split()

            server = smtplib.SMTP()
            server.connect(smtp_host, smtp_port)
            server.ehlo()
            if self.config.get('SMTP', 'use_tls') == 'true':
                server.starttls()

            if self.config.get('SMTP', 'need_login') == 'true':
                server.login(smtp_user, smtp_password)

            msg = MIMEMultipart()
            msg['From'] = smtp_from
            msg['To'] = COMMASPACE.join(smtp_tolist)
            msg['Subject'] = self.parse_string(smtp_subject)
            msg.attach(MIMEText(self.parse_string(smtp_text), 'html'))
            msg.attach(MIMEText('\nsent by:\n'+metadata.epilog, 'plain'))
            server.sendmail(smtp_from, smtp_tolist, msg.as_string())
            server.quit()
        except:
            logger.exception("couldn't send email")

        return True

    def load_config(self, configfile):
        logger.debug("load_config (%s)",configfile)
        logger.debug("use configfile: %s", configfile.name)
        config = ConfigParser.ConfigParser()
        config.read(configfile.name)
        if not config.sections():
            logger.info("founded empty configfile - start write_demo_configfile")
            configfile.close()
            raise Exception("No valid configfile found at "+configfile)

        return conf.config_object.ConfigObject(config)

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
                input_pins = self.config.get_keys('InputPins'),
                output_pins = self.config.get_keys('OutputPins')
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

    def parse_string(self, input_string):
        parsed_string = datetime.datetime.now().strftime(input_string)

        if self.keyboard is not None:
            self.additional_informations['LastKey'] = str(self.keyboard.last_key)

        parsed_string = parsed_string.replace(
            "!INFOS_PLAIN!",
            str(self.__additional_informations)
        )

        infos_as_html = '<table>'
        for key in self.__additional_informations.keys():
            infos_as_html += '<tr><td>'
            infos_as_html += '<b>'+key+'</b>'
            infos_as_html += '</td><td>'
            infos_as_html += '<i>'+cgi.escape(
                str(self.__additional_informations.get(key)).replace("\r\n", "<br />")
            )+'</i>'
            infos_as_html += '</td></tr>'
        infos_as_html = '</table>'

        parsed_string = parsed_string.replace(
            "!INFOS!",
            infos_as_html
        )

        for key in self.__additional_informations.keys():
            parsed_string = parsed_string.replace(
                "!"+key+"!",
                str(self.__additional_informations[key])
            )

        return parsed_string