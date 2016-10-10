#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)
REQUIREMENT = dict(
    fulfilled_with_one = False,
    text_description = 'Alle Module vom Bereich System sind für den Betrieb von DoorPi an verschiedenen Stellen zwingend nötig.',
    events = [
        #dict( name = 'OnWebServerStart', description = 'Der Webserver ist gestartet. Somit stehen die Webservices und die Weboberfläche zur Verfügung. Standardmäßig wird Port 80 benutzt (Parameter ip und port)'),
    ],
    configuration = [
        #dict( section = DOORPIWEB_SECTION, key = 'ip', type = 'string', default = '', mandatory = False, description = 'IP-Adresse an die der Webserver gebunden werden soll (leer = alle)'),
    ],
    libraries = dict(
        importlib = dict(
            text_warning =          '',
            text_description =      'Das Python-Modul importlib wird zum dynamischen Laden von Dateien genutzt. So sind z.B. alle Actions jeweils als eigene Datei abgelegt die anhand des Dateinamens (= Name der Action) geladen werden, wenn diese auch wirklich benötigt werden. So muss am restlichen Quellcode keine Anpassung gemacht werden und es reicht eine neue Aktion bereit zu stellen.',
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
            text_description =      'Das Python-Modul os gibt DoorPi die Möglichkeit mit dem System zu kommunizieren, auf dem es läuft.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/os.html'
            }
        ),
        logging = dict(
            text_warning =          '',
            text_description =      '''
Das Python-Modul logging wird in DoorPi genutzt um die Log-Ausgaben, also die Status-Meldungen von DoorPi, an die gewünschten Stellen zu schreiben.
Im Anwendungsmodus wird keine Log-Datei geschrieben, sondern nur die Log-Ausgabe am Bildschrim angezeigt.
Im Daemon-Modus allerdings wird eine Log-Datei geschrieben (<a href="https://github.com/motom001/DoorPi/blob/master/doorpi/main.py#L15">/var/log/doorpi/doorpi.log</a>)
Die maximale Größe der Logdatei ist auf 50000 Bytes festgelegt. Danach wird die Log-Datei umbenannt (Backup der Log) und eine neue geschrieben.
Es gibt jedoch max. die 10 letzten Log-Dateien - alle älteren werden verworfen.
''',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/logging.html'
            }
        ),
        re = dict(
            text_warning =          '',
            text_description =      'Das Python-Modul re wird für reguläre Ausdrücke genutzt. Diese kommen unter anderem im Bereich des Webservers zum Einsatz.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/re.html'
            }
        ),
        json = dict(
            text_warning =          '',
            text_description =      'Das Python-Modul json ermöglicht DoorPi die internen Objekte in lesbare JSON-String umzuwandeln und später auszugeben. Vor allem im Bereich vom Webserver werden so die Webservices aufbereitet.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/json.html'
            }
        ),
        time = dict(
            text_warning =          '',
            text_description =      'Das Python-Modul time bietet die Funktion sleep die als Action sowie an einigen anderen Stellen innerhalb von DoorPi genutzt wird.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/time.html'
            }
        ),
        math = dict(
            text_warning =          '',
            text_description =      'Das Python-Modul math wird zusammen mit wave und array genutzt um den DialTone zu erzeugen.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/math.html'
            }
        ),
        wave = dict(
            text_warning =          '',
            text_description =      'Das Python-Modul wave wird zusammen mit math und array genutzt um den DialTone zu erzeugen.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/wave.html'
            }
        ),
        array = dict(
            text_warning =          '',
            text_description =      'Das Python-Modul array wird zusammen mit math und wave genutzt um den DialTone zu erzeugen.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/array.html'
            }
        ),
        sys = dict(
            text_warning =          '',
            text_description =      'Das Python-Modul sys gibt DoorPi die Möglichkeit mit dem System zu kommunizieren, auf dem es läuft.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/sys.html'
            }
        ),
        argparse = dict(
            text_warning =          '',
            text_description =      'Das Python-Modul argparse wird genutzt um die Parameter beim DoorPi-Start auswerten zu können.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/argparse.html'
            }
        ),
        datetime = dict(
            text_warning =          '',
            text_description =      'Das Python-Modul datetime wird genutzt um Zeitstempel erzeugen zu können.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/datetime.html'
            }
        ),
        cgi = dict(
            text_warning =          '',
            text_description =      'Das Python-Modul cgi wird unter anderem zum Parsen von POST-Anfragen beim Webserver benötigt.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/cgi.html'
            }
        ),
        resource = dict(
            text_warning =          '',
            text_description =      'Das Python-Modul resource ermögict Abfragen des System-Zustand, auf dem DoorPi läuft.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/resource.html'
            }
        ),
        random = dict(
            text_warning =          '',
            text_description =      'Das Python-Modul random ermöglicht die Erstellung von Zufallszahlen / Zufallszeichenketten (z.B. Event-ID)',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/random.html'
            }
        ),
        string = dict(
            text_warning =          '',
            text_description =      'Das Python-Modul string wird zur Manipulation von Zeichenketten genutzt.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um eine Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, in dem im Python-Interpreter <code>import importlib</code> eingeben wird.',
            text_configuration =    '',
            configuration = [
                #dict( section = 'DoorPi', key = 'eventlog', type = 'string', default = '!BASEPATH!/conf/eventlog.db', mandatory = False, description = 'Ablageort der SQLLite Datenbank für den Event-Handler.')
            ],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/string.html'
            }
        )
    )
)
