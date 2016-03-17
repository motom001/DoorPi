# -*- coding: utf-8 -*-

from main import DOORPI
from plugins.interfaces.docs import DOCUMENTATION as INTERFACE_BASE_CLASS_DOCUMENTATION

CHANNEL_EVENT_PARAMETER = [
    dict( name = 'class_name', type = 'string', mandatory = True, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'module_name', type = 'string',  mandatory = True, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'interface_name', type = 'string',  mandatory = True, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'interface_id', type = 'string',  mandatory = True, description = 'Parameter 1 der zur Aktion übergeben wird' ),
]
#initial_value = False, log = True, high_level = True, low_level = False, high_by_event = None, low_by_event = None
INPUT_CHANNEL_EVENT_PARAMETER = [
    dict( name = 'id', type = 'string', default = 'sqllite', mandatory = True, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'name', type = 'string', default = 'sqllite', mandatory = True, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'technical_name', type = 'string', default = 'sqllite', mandatory = True, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'value', type = 'string', default = 'False', mandatory = True, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'initial_value', type = 'string', default = 'sqllite', mandatory = True, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'log', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'high_level', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'low_level', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'high_by_event', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'low_by_event', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' )
] + CHANNEL_EVENT_PARAMETER

OUTPUT_CHANNEL_EVENT_PARAMETER = [
    dict( name = 'id', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'name', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'technical_name', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'value', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'initial_value', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'log', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'high_level', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'low_level', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'high_by_event', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ),
    dict( name = 'low_by_event', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ),
] + CHANNEL_EVENT_PARAMETER

DOCUMENTATION = copy.deepcopy(INTERFACE_BASE_CLASS_DOCUMENTATION).update(dict(
    fulfilled_with_one = False,
    text_description = 'Basis Klasse der Hardware-Interfaces',
    actions = [
        dict( name = 'SetChannel', description = "", parameter = OUTPUT_CHANNEL_EVENT_PARAMETER),
    ],
    events = [
        dict( name = 'OnInputActive', description = 'Wird ausgelöst, wenn ein input channel HIGH-Pegel liefert (HIGH_LEVEL: %s)'%DOORPI.CONST.HIGH_LEVEL, parameter = INPUT_CHANNEL_EVENT_PARAMETER),
        dict( name = 'OnInputInactive', description = 'Wird ausgelöst, wenn ein input channel LOW-Pegel liefert (LOW_LEVEL: %s)'%DOORPI.CONST.LOW_LEVEL, parameter = INPUT_CHANNEL_EVENT_PARAMETER),
        dict( name = 'OnInputChange', description = 'Wird ausgelöst, wenn ein input channel sich verändert', parameter = INPUT_CHANNEL_EVENT_PARAMETER),
        dict( name = 'Vorlage', description = '', parameter = [ dict( name = 'param1', type = 'string', default = 'sqllite', mandatory = False, description = 'Parameter 1 der zur Aktion übergeben wird' ) ]),
    ],
    configuration = [
        #dict( section = DOORPIWEB_SECTION, key = 'ip', type = 'string', default = '', mandatory = False, description = 'IP-Adresse an die der Webserver gebunden werden soll (leer = alle)'),
    ],
    libraries = dict()
))
