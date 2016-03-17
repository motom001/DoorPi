# -*- coding: utf-8 -*-

from main import DOORPI

DOCUMENTATION = dict(
    fulfilled_with_one=False,
    text_description='Modul zur Verwaltung der Konfiguration für DoorPi und zum Laden der Documentation pro Modul',
    events=[
        # dict( name = 'Vorlage', description = '', parameter = [ dict( name = 'param1', type = 'string',
        # default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ) ]),
    ],
    configuration=[
        # dict( section = DOORPIWEB_SECTION, key = 'ip', type = 'string', default = '', mandatory = False,
        # description = 'IP-Adresse an die der Webserver gebunden werden soll (leer = alle)'),
    ],
    libraries=dict(
        importlib=DOORPI.libraries['importlib'],
        json=DOORPI.libraries['json']
    )
)
