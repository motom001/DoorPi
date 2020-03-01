# -*- coding: utf-8 -*-
import doorpi
from doorpi.action.base import SingleAction

import requests
import json
from requests.auth import HTTPBasicAuth

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)


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
       'method': method,
       'params': parameters,
       'jsonrpc': config['jsonrpc'],
       'id': 0, }
    return requests.post(
        config['webservice_url'],
        headers = config['headers'],
        auth = HTTPBasicAuth(config['username'], config['password']),
        data = json.dumps(payload))

def ips_rpc_check_variable_exists(key, config=None):
    if config is None:
        config = ips_rpc_create_config()
    response = ips_rpc_fire('IPS_VariableExists', config, key)
    return response.json['result']

def ips_rpc_get_variable_type(key, config=None):
    if config is None:
        config = ips_rpc_create_config()
    response = ips_rpc_fire('IPS_GetVariable', config, key)
    return response.json['result']['VariableValue']['ValueType']

def ips_rpc_get_variable_value(key, config=None):
    if config is None:
        config = ips_rpc_create_config()
    response = ips_rpc_fire('GetValue', config, key)
    return response.json['result']

def ips_rpc_call_phonenumber_from_variable(key, config=None):
    try:
        if config is None:
            config = ips_rpc_create_config()
        if ips_rpc_check_variable_exists(key, config) is not True:
            raise Exception('no variable %s', key)
        type = ips_rpc_get_variable_type(key, config)
        if type is None:
            raise Exception('type of variable %s unknown', key)
        # variable types (0: boolean, 1: integer, 2: float, 3: string)
        elif type is not 3:
            raise Exception("type of variable %s is not a string", key)

        phonenumber = ips_rpc_get_variable_value(key, config)
        logger.debug('fire now sipphone.call for this number: %s', phonenumber)
        doorpi.DoorPi().sipphone.call(phonenumber)
        logger.debug('finished sipphone.call for this number: %s', phonenumber)
    except Exception as ex:
        logger.exception('couldn\'t get phonenumber from IpsRpc (%s)', ex)
        return False
    return True

def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) is not 1:
        return None

    key = int(parameter_list[0])
    return IpsRpcCallPhonenumberFromVariableAction(ips_rpc_call_phonenumber_from_variable, key)


class IpsRpcCallPhonenumberFromVariableAction(SingleAction):
    pass
