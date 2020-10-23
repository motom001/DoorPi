"""Actions that interact with the Symcon IPS v3: symcon_ips3"""
import enum
import json
import logging
from typing import Any, Dict, Mapping, TypedDict

import requests

import doorpi

from . import Action, action

LOGGER = logging.getLogger(__name__)
TRUE_VALUES = {"true", "yes", "on", "1"}


# Relevant documentation (german):
# <https://www.symcon.de/service/dokumentation/befehlsreferenz/variablenverwaltung/ips-getvariable/>
@enum.unique
class IPSVariableType(enum.Enum):
    """Types of variables known to Symcon IPS v3"""

    BOOLEAN = 0
    INTEGER = 1
    FLOAT = 2
    STRING = 3


class IPSConfig(TypedDict):
    webservice_url: str
    username: str
    password: str


class IPSConnector:
    """Helper class that facilitates connecting to a Symcon IPS"""

    @property
    def config(self) -> IPSConfig:
        """Retrieves the IPS config from DoorPi."""
        dcfg = doorpi.INSTANCE.config.view("ip_symcon")
        return IPSConfig(
            webservice_url=dcfg["server"],
            username=dcfg["username"],
            password=dcfg["password"],
        )

    def _do_request(self, method: str, *prm: Any) -> Dict[str, Any]:
        payload = json.dumps(
            {"method": method, "params": prm, "jsonrpc": "2.0", "id": 0}
        ).encode("utf-8")

        response = requests.post(
            self.config["webservice_url"],
            data=payload,
            headers={"Content-Type": "application/json"},
            auth=(self.config["username"], self.config["password"]),
        )

        return json.loads(response.content.decode("utf-8"))

    def variable_exists(self, key: int) -> bool:
        """Checks whether a variable exists."""
        return self._do_request("IPS_VariableExists", key)["result"]

    def variable_type(self, key: int) -> IPSVariableType:
        """Returns the type of the named variable."""
        if not self.variable_exists(key):
            raise KeyError(f"Variable {key} does not exist")
        response = self._do_request("IPS_GetVariable", key)
        vartype = response["result"]["VariableValue"]["ValueType"]
        if vartype is None:
            raise RuntimeError(f"Couldn't determine type of variable {key}")
        return IPSVariableType(int(vartype))

    def set_value(self, key: int, value: Any) -> None:
        """Sets variable ``key`` to ``value``."""
        vartype = self.variable_type(key)
        if vartype is IPSVariableType.BOOLEAN:
            value = value.lower().strip() in TRUE_VALUES
        elif vartype is IPSVariableType.INTEGER:
            value = int(value)
        elif vartype is IPSVariableType.FLOAT:
            value = float(value)
        elif vartype is IPSVariableType.STRING:
            value = str(value)
        else:
            raise RuntimeError(f"Unknown variable type {vartype}")

        self._do_request("SetValue", key, value)

    def get_value(self, key: int) -> Any:
        """Retrieves a variable from the IPS."""
        return self._do_request("GetValue", key)["result"]


class IPSSetValueAction(IPSConnector, Action):
    """Sets a variable in the IPS."""

    def __init__(self, key: str, value: str) -> None:
        super().__init__()
        self.__key = int(key)
        self.__value = value

    def __call__(self, event_id: str, extra: Mapping[str, Any]) -> None:
        self.set_value(self.__key, doorpi.INSTANCE.parse_string(self.__value))

    def __str__(self) -> str:
        return f"Set IPS variable {self.__key} to {self.__value}"

    def __repr__(self) -> str:
        return f"symcon_ips3:set,{self.__key},{self.__value}"


class IPSCallFromVariableAction(IPSConnector, Action):
    """Calls the number that is stored in the IPS."""

    def __init__(self, key: str) -> None:
        super().__init__()
        self.__key = int(key)

    def __call__(self, event_id: str, extra: Mapping[str, Any]) -> None:
        vartype = self.variable_type(self.__key)
        if vartype is not IPSVariableType.STRING:
            raise ValueError(f"Variable {self.__key} is not a string")
        uri = self.get_value(self.__key)

        LOGGER.info(
            "[%s] Got phone number %s from variable %s",
            event_id,
            repr(uri),
            self.__key,
        )
        doorpi.INSTANCE.sipphone.call(uri)

    def __str__(self) -> str:
        return f"Call the number stored in IPS variable {self.__key}"

    def __repr__(self) -> str:
        return f"symcon_ips3:call,{self.__key}"


@action("symcon_ips3")
def instantiate(ipsaction: str, *params: str) -> Action:
    """Creates the action named by ``ipsaction``."""
    try:
        cls = {
            "set": IPSSetValueAction,
            "call": IPSCallFromVariableAction,
        }[ipsaction]
    except KeyError:
        raise ValueError(f"Unknown IPS RPC action {ipsaction}") from None
    return cls(*params)
