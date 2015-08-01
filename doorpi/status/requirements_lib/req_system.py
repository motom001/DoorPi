#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

REQUIREMENT = dict(
    fulfilled_with_one = False,
    text_description = '',
    events = [
        #dict( name = 'OnWebServerStart', description = 'Der Webserver ist gestartet. Somit stehen die Webservices und die Weboberfläche zur Verfügung. Standardmäßig wird Port 80 benutzt (Parameter ip und port)'),
    ],
    configuration = [
        #dict( section = DOORPIWEB_SECTION, key = 'ip', type = 'string', default = '', mandatory = False, description = 'IP-Adresse an die der Webserver gebunden werden soll (leer = alle)'),
    ],
    libraries = dict(
        importlib = dict(
            text_warning =          '',
            text_description =      '',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import BaseHTTPServer</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/importlib.html'
            }
        ),
        os = dict(
            text_warning =          '',
            text_description =      '',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/importlib.html'
            }
        ),
        logging = dict(
            text_warning =          '',
            text_description =      '',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/importlib.html'
            }
        ),
        re = dict(
            text_warning =          '',
            text_description =      '',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/importlib.html'
            }
        ),
        json = dict(
            text_warning =          '',
            text_description =      '',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/importlib.html'
            }
        ),
        time = dict(
            text_warning =          '',
            text_description =      '',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/importlib.html'
            }
        ),
        math = dict(
            text_warning =          '',
            text_description =      '',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/importlib.html'
            }
        ),
        wave = dict(
            text_warning =          '',
            text_description =      '',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/importlib.html'
            }
        ),
        array = dict(
            text_warning =          '',
            text_description =      '',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/importlib.html'
            }
        ),
        sys = dict(
            text_warning =          '',
            text_description =      '',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/importlib.html'
            }
        ),
        argparse = dict(
            text_warning =          '',
            text_description =      '',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/importlib.html'
            }
        ),
        datetime = dict(
            text_warning =          '',
            text_description =      '',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/importlib.html'
            }
        ),
        cgi = dict(
            text_warning =          '',
            text_description =      '',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/importlib.html'
            }
        ),
        resource = dict(
            text_warning =          '',
            text_description =      '',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/importlib.html'
            }
        ),
        random = dict(
            text_warning =          '',
            text_description =      '',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/importlib.html'
            }
        ),
        string = dict(
            text_warning =          '',
            text_description =      '',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/importlib.html'
            }
        )
    )
)

