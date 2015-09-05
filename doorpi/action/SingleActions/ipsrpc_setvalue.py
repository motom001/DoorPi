#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import doorpi
import requests
import json
from requests.auth import HTTPBasicAuth
from doorpi.action.base import SingleAction

def ips_rpc_create_config():
    config = {}
    config['webservice_url'] = doorpi.DoorPi().config.get('IP-Symcon', 'server')
    config['username'] = doorpi.DoorPi().config.get('IP-Symcon', 'username')
    config['password'] = doorpi.DoorPi().config.get('IP-Symcon', 'password')
    config['jsonrpc'] = doorpi.DoorPi().config.get('IP-Symcon', 'jsonrpc', '2.0')
    config['headers'] = {'content-type': 'application/json'}
    return config

def ips_rpc_fire(method, config, *parameters):
    payload = {
       "method": method,
       "params": parameters,
       "jsonrpc": config['jsonrpc'],
       "id": 0,
    }
    return requests.post(
        config['webservice_url'],
        headers = config['headers'],
        auth = HTTPBasicAuth(config['username'], config['password']),
        data = json.dumps(payload)
    )

def ips_rpc_check_variable_exists(key, config = None):
    if config is None: config = ips_rpc_create_config()
    response = ips_rpc_fire('IPS_VariableExists', config, key)
    return response.json['result']

def ips_rpc_get_variable_type(key, config = None):
    if config is None: config = ips_rpc_create_config()
    response = ips_rpc_fire('IPS_GetVariable', config, key)
    return response.json['result']['VariableValue']['ValueType']

def ips_rpc_set_value(key, value, config = None):
    try:
        if config is None: config = ips_rpc_create_config()
        if ips_rpc_check_variable_exists(key, config) is not True: raise Exception("var %s doesn't exist", key)
        type = ips_rpc_get_variable_type(key, config)
        if type is None: raise Exception("type of var %s couldn't find", key)
        # http://www.ip-symcon.de/service/dokumentation/befehlsreferenz/variablenverwaltung/ips-getvariable/
        # Variablentyp (0: Boolean, 1: Integer, 2: Float, 3: String)
        elif type == 0:
            if value.lower() in ['true', 'yes', '1']: value = True
            else: value = False
        elif type == 1: value = int(value)
        elif type == 2: value = float(value)
        elif type == 3: value = str(value)
        else: value = str(value)
        ips_rpc_fire('SetValue', config, key, value)
    except Exception as ex:
        logger.exception("couldn't send IpsRpc (%s)", ex)
        return False
    return True

def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) is not 2: return None

    key = int(parameter_list[0])
    value = parameter_list[1]

    return IpsRpcSetValueAction(ips_rpc_set_value, key, value)

class IpsRpcSetValueAction(SingleAction):
    pass