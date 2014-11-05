#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import sys
import argparse
import time # used by: DoorPi.run
import ConfigParser # used by: DoorPi.load_config
import os # used by: DoorPi.load_config
import BaseHTTPServer
from string import Template

import metadata
import conf.config_object
import HTTPRequest_Handler

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class DoorPiWeb(object):
    __metaclass__ = Singleton

    __config = None
    def get_config(self):
        return self.__config

    __HTTPRequestHandler = None
    def get_HTTPRequestHandler(self):
        return self.__HTTPRequestHandler

    __Sessions = {}
    def get_sessions(self):
        return self.__Sessions

    def get_session(self, session_id):
        if remote_client in self.__Sessions: return self.__Sessions[session_id]
        else: return None

    def exists_session(self, remote_client):
        return remote_client in self.__Sessions

    #def set_Sessions(self, remote_client):

    __prepared = False

    def __init__(self):
        logger.debug("__init__")
        # for start as daemon - if start as app it will not matter to load this vars
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path =  '/var/run/doorpi.pid'
        self.pidfile_timeout = 5

    def prepare(self):
        logger.debug("prepare")

        parsed_arguments = self.parse_argv()
        logger.debug("given arguments argv: %s", parsed_arguments)

        if not parsed_arguments.configfile and not self.__config:
            raise Exception("no config exists an no new given")

        self.__config = self.load_config(parsed_arguments.configfile)
        self.check_config()
        self.__prepared = True
        logger.debug(self.build_security_object('motom001', '127.0.0.1'))
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
        if self.__HTTPRequestHandler is not None:
            self.__HTTPRequestHandler.socket.close()
            self.__HTTPRequestHandler = None
            del self.__HTTPRequestHandler

    def run(self):
        logger.debug("run")
        if not self.__prepared: self.prepare()

        self.__HTTPRequestHandler = BaseHTTPServer.HTTPServer(('', 8080), HTTPRequest_Handler.DoorPiWeb_HTTPRequestHandler)
        self.__HTTPRequestHandler.serve_forever()
        self.__HTTPRequestHandler.server_close()

        return self

    def load_config(self, configfile):
        logger.debug("load_config (%s)",configfile)
        logger.debug("use configfile: %s", configfile.name)
        config = ConfigParser.ConfigParser()
        config.read(configfile.name)
        #if not config.sections():
        #    logger.info("founded empty configfile - start write_demo_configfile")
        #    configfile.close()
        #    os.remove(configfile.name)
        #    config = self.write_demo_configfile(configfile.name)

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
        config.set('InputPins', '0', 'call:00493515555555')
        config.add_comment('InputPins','multicall_pin','[call:[phonenumber], call:[phonenumber]] # make a call to all this numbers, first answer wins')
        config.set('InputPins', '1', 'call:00493515555555')
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
        config.set('AdminNumbers', '00493515555555', 'active')

        #config.add_section('Log-File')
        #config.set('Log-File', 'Logfile', configfilename)
        #config.set('Log-File', 'Loglevel', 'DEBUG')

        with open(config_filename, 'wb') as configfile:
            config.write(configfile)
        return config

    def create_session_id(self, socket):
        return socket.client_address

    def set_defaults_to_html(self, file_content):
        default_replacements = dict(
            html_epilog = metadata.html_epilog
        )

        return Template(file_content).safe_substitute(default_replacements)

    def get_content(self, socket, requested_file):
        logger.debug("getContent for file %s", requested_file)

        session_id = self.create_session_id(socket)
        www = self.get_config().get_string('DoorPiWeb', 'www', '/home/pi/DooPiWeb/www')

        # favicon.ico
        if requested_file.endswith('favicon.ico'):
            if not self.exists_session(session_id):
                return open(www + '/lib/images/favicon_red.ico', 'r').readlines()
            else:
                return open(www + '/lib/images/favicon_green.ico', 'r').readlines()

        if not self.exists_session(session_id):
            logger.debug("no session with id %s exists", session_id)

        content = open(requested_file, 'r').readlines()
        return self.set_defaults_to_html('\n'.join(content))

    def check_config(self):
        groups_with_write_permissions = self.get_config().get_keys('WritePermission')
        groups_with_read_permissions = self.get_config().get_keys('ReadPermission')
        groups = self.get_config().get_keys('Group')
        users = self.get_config().get_keys('User')

        if len(groups) == 0:
            logger.error("no groups in configfile!")

        if len(groups_with_write_permissions) == 0:
            logger.warning("no WritePermission founded")
        for group in groups_with_write_permissions:
            if group not in groups: logger.warning("group %s doesn't exists but is assigned to WritePermission", group)

        if len(groups_with_read_permissions) == 0:
            logger.info("no ReadPermission founded")
        for group in groups_with_read_permissions:
            if group not in groups: logger.warning("group %s doesn't exists but is assigned to ReadPermission", group)

        for group in groups:
            users_in_group = self.get_config().get_string('Group', group).split(',')
            for user_in_group in users_in_group:
                if user_in_group not in users:
                    logger.warning("user %s is assigned to group %s but doesn't exist as user", user_in_group, group)

        www_app = self.get_config().get_string('DoorPiWeb', 'www', '/home/pi/DooPiWeb/www')+'/app/'
        for group in groups_with_write_permissions:
            modules = self.get_config().get_string('WritePermission', group).split(',')
            for module in modules:
                if not os.path.isdir(www_app+module): logger.warning("modul %s doesn't exist but is assigned to group %s in WritePermission", module, group)

        for group in groups_with_read_permissions:
            modules = self.get_config().get_string('ReadPermission', group).split(',')
            for module in modules:
                if not os.path.isdir(www_app+module): logger.warning("modul %s doesn't exist but is assigned to group %s in ReadPermission", module, group)


    def build_security_object(self, username, remote_client = ''):
        WebSession = dict(
            username = username,
            remote_client = remote_client,
            session_starttime = time.time(),
            readpermission = [],
            writepermissions = [],
            groups = []
        )

        groups_with_write_permissions = self.get_config().get_keys('WritePermission')
        groups_with_read_permissions = self.get_config().get_keys('ReadPermission')
        groups = self.get_config().get_keys('Group')
        users = self.get_config().get_keys('User')

        if not username in users: return WebSession

        for group in groups:
            users_in_group = self.get_config().get_string('Group', group).split(',')
            if username in users_in_group: WebSession['groups'].append(group)

        for group in groups_with_read_permissions:
            if group in WebSession['groups']:
                modules = self.get_config().get_string('ReadPermission', group).split(',')
                WebSession['readpermission'].extend(modules)

        for group in groups_with_write_permissions:
            if group in WebSession['groups']:
                modules = self.get_config().get_string('WritePermission', group).split(',')
                WebSession['writepermissions'].extend(modules)

        WebSession['readpermission'] = list(set(WebSession['readpermission']))
        WebSession['readpermission'].sort()
        WebSession['writepermissions'] = list(set(WebSession['writepermissions']))
        WebSession['writepermissions'].sort()

        return WebSession

    def build_navigation(self, socket):
        session = self.get_session(self.create_session_id(socket))
        self.get_config().get_string(session.username)
        return ''