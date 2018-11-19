#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)



REQUIREMENT = dict(
    fulfilled_with_one = True,
    text_description = '',
    events = [],
    configuration = [],
    libraries = dict(
        configparser = dict(
            text_warning =          '',
            text_description =      'Das Config-Modul wird benötigt um alle Einstellungen in einer Datei abspeichern und später wieder laden zu können.',
            text_installation =     'Eine Installation ist nicht nötig, da es sich hierbei um ein Python-Standard-Modul handelt.',
            auto_install =          False,
            text_test =             'Der Status kann gestestet werden, indem im Python-Interpreter <code>import configparser</code> eingeben wird.',
            text_configuration =    '''Eine Konfiguration als Eintrag in der Konfigurationsdatei hat logischerweise keinen Sinn.
Deshalb kann die zu nutzende Config-Datei als Parameter (--configfile) beim DoorPi Start mitgegeben werden. Beispiel:
<code>doorpi_cli --configfile /etc/doorpi/doorpi.ini</code>

Wenn der Parameter wegelassen wird, sucht der ConfigParser automatisch nach folgenden Dateien (wobei !BASEPATH! das aktuelle Verzeichnis ist)

<ol>
    <li>!BASEPATH!/conf/doorpi.ini</li>
    <li>!BASEPATH!/conf/doorpi.cfg</li>
</ol>

Sollte keine Datei vorhanden sein, so wird DoorPi mit Standardwerten gestartet und die Konfigurationsdatei an der ersten möglichen Stelle abgespeichert.
''',
            configuration = [],
            text_links = {
                'docs.python.org': 'https://docs.python.org/2.7/library/configparser.html'
            }
        )
    )
)

