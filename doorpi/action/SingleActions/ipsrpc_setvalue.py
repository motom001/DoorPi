# -*- coding: utf-8 -*-
import doorpi
from doorpi.action.base import SingleAction

import requests
from requests.auth import HTTPBasicAuth
import json

import logging
logger = logging.getLogger(__name__)
logger.debug('%s loaded', __name__)


def ips_rpc_create_config():
    config = {}
    config['webservice_url'] = doorpi.DoorPi(
    ).config.get('IP-Symcon', 'server')
    config['username'] = doorpi.DoorPi().config.get('IP-Symcon', 'username')
    config['password'] = doorpi.DoorPi().config.get('IP-Symcon', 'password')
    config['jsonrpc'] = doorpi.DoorPi().config.get(
        'IP-Symcon', 'jsonrpc', '2.0')
    config['headers'] = {'content-type': 'application/json'}
    return config


def ips_rpc_fire(method, config, *parameters):
    payload = json.dumps({
        'method': method,
        'params': parameters,
        'jsonrpc': config['jsonrpc'],
        'id': 0}).encode('utf-8')
    response = requests.post(
        config['webservice_url'],
        headers=config['headers'],
        auth=HTTPBasicAuth(config['username'], config['password']),
        data=payload)
    return json.loads(response.content.decode('utf-8'))


def ips_rpc_check_variable_exists(key, config=None):
    if config is None:
        config = ips_rpc_create_config()
    return ips_rpc_fire('IPS_VariableExists', config, key)['result']


def ips_rpc_get_variable_type(key, config=None):
    if config is None:
        config = ips_rpc_create_config()
    result = ips_rpc_fire('IPS_GetVariable', config, key)
    return result['result']['VariableValue']['ValueType']


def ips_rpc_set_value(key, value, config=None):
    try:
        if config is None:
            config = ips_rpc_create_config()
        if ips_rpc_check_variable_exists(key, config) is not True:
            raise Exception('no variable %s found', key)
        type = ips_rpc_get_variable_type(key, config)
        if type is None:
            raise Exception('type of variable %s unknown', key)
        # variable type (0: boolean, 1: integer, 2: float, 3: string)
        elif type == 0:
            value = (value.lower() in ['true', 'yes', '1'])
        elif type == 1:
            value = int(value)
        elif type == 2:
            value = float(value)
        else:
            value = str(value)
        ips_rpc_fire('SetValue', config, key, value)
    except Exception as ex:
        logger.exception('send IpsRpc (%s) failed', ex)
        return False
    return True


def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) != 2:
        return None

    key = int(parameter_list[0])
    value = parameter_list[1]
    return IPSRpcSetValueAction(ips_rpc_set_value, key, value)


class IPSRpcSetValueAction(SingleAction):
    pass
