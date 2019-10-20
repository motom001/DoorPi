import enum
import json
import logging
import requests

import doorpi
from doorpi.actions import Action


logger = logging.getLogger(__name__)
TRUE_VALUES = ("true", "yes", "on", "1")


# Relevant documentation (german):
# https://www.symcon.de/service/dokumentation/befehlsreferenz/variablenverwaltung/ips-getvariable/
@enum.unique
class IPSVariableType(enum.Enum):
    BOOLEAN = 0
    INTEGER = 1
    FLOAT = 2
    STRING = 3


class IPSConnector:

    @property
    def config(self):
        dcfg = doorpi.DoorPi().config
        config = {
            "webservice_url": dcfg.get_string("IP-Symcon", "server"),
            "username": dcfg.get_string("IP-Symcon", "username"),
            "password": dcfg.get_string("IP-Symcon", "password"),
        }
        return config

    def _do_request(self, method, *prm):
        payload = json.dumps({
            "method": method,
            "params": prm,
            "jsonrpc": "2.0",
            "id": 0
        }).encode("utf-8")

        response = requests.post(
            self.config["webservice_url"],
            data=payload,
            headers={"Content-Type": "application/json"},
            auth=(self.config["username"], self.config["password"]),
        )

        return json.loads(response.content.decode("utf-8"))

    def variable_exists(self, key):
        return self._do_request("IPS_VariableExists", key)["result"]

    def variable_type(self, key):
        if not self.variable_exists(key):
            raise KeyError(f"Variable {key} does not exist")
        return self._do_request("IPS_GetVariable", key)["result"]["VariableValue"]["ValueType"]

    def set_value(self, key, value):
        vartype = self.variable_type(key)
        if vartype is None:
            raise RuntimeError(f"Couldn't determine type of variable {key}")
        vartype = IPSVariableType(int(vartype))
        if vartype == IPSVariableType.BOOLEAN:
            value = value.lower().strip() in TRUE_VALUES
        elif vartype == IPSVariableType.INTEGER:
            value = int(value)
        elif vartype == IPSVariableType.FLOAT:
            value = float(value)
        elif vartype == IPSVariableType.STRING:
            value = str(value)
        else: raise RuntimeError(f"Unknown variable type {vartype}")

        self._do_request("SetValue", key, value)

    def get_value(self, key):
        return self._do_request("GetValue", key)["result"]


class IPSSetValueAction(IPSConnector, Action):

    def __init__(self, key, value):
        self.__key = int(key)
        self.__value = value

    def __call__(self, event_id, extra):
        self.set_value(self.__key, doorpi.DoorPi().parse_string(self.__value))


class IPSCallFromVariableAction(IPSConnector, Action):

    def __init__(self, key):
        self.__key = int(key)

    def __call__(self, event_id, extra):
        vartype = self.variable_type(self.__key)
        if vartype != 3:
            raise ValueError(f"Variable {self.__key} is not a string")
        uri = self.get_value(self.__key)

        logger.info("[%s] Got phone number %s from variable %s", event_id, repr(uri), self.__key)
        doorpi.DoorPi().sipphone.call(uri)


def instantiate(action, *params):
    if action == "set": return IPSSetValueAction(*params)
    elif action == "call": return IPSCallFromVariableAction(*params)
    else: raise ValueError(f"Unknown IPS RPC action {action}")
