#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import doorpi
import requests
import json
from requests.auth import HTTPBasicAuth
from action.base import SingleAction

def ips_rpc_set_value(method, key, value):
    try:
        url = doorpi.DoorPi().config.get('IP-Symcon', 'server')
        auth = HTTPBasicAuth(
            doorpi.DoorPi().config.get('IP-Symcon', 'username'),
            doorpi.DoorPi().config.get('IP-Symcon', 'password')
        )
        headers = {'content-type': 'application/json'}
        payload = {
           "method": method,
           "params": [key, value],
           "jsonrpc": doorpi.DoorPi().config.get('IP-Symcon', 'jsonrpc', '2.0'),
           "id": 0,
        }
        response = requests.post(
            url,
            headers = headers,
            auth = auth,
            data = json.dumps(payload)
        )
        logger.debug(response.json)

    except Exception as ex:
        logger.exception("couldn't send IpsRpc (%s)", ex)
        return False
    return True

def get(parameters):
    parameter_list = parameters.split(',')
    if len(parameter_list) is not 2: return None

    key = int(parameter_list[0])
    value = parameter_list[1].lower() in ['true', 'yes', '1']

    return IpsRpcSetValueAction(ips_rpc_set_value, "SetValue", key, value)

class IpsRpcSetValueAction(SingleAction):
    pass