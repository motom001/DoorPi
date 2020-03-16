from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase
from unittest.mock import patch, MagicMock

import doorpi.actions.symcon_ips3 as action
from doorpi.actions.symcon_ips3 import IPSVariableType

import json


class DummyResponse:

    def __init__(self, content):
        self.content = content


def fake_post(*args, data, **kw):
    d = json.loads(data.decode("utf-8"))

    if d["method"] == "IPS_VariableExists":
        return DummyResponse(json.dumps({"result": True}).encode("utf-8"))
    elif d["method"] == "IPS_GetVariable":
        return DummyResponse(json.dumps({"result": {
            "VariableValue": {
                "ValueType": IPSVariableType.STRING.value,
            },
        }}).encode("utf-8"))
    elif d["method"] == "GetValue":
        return DummyResponse(json.dumps({"result": "**1"}).encode("utf-8"))
    elif d["method"] == "SetValue":
        return DummyResponse(json.dumps({"result": True}).encode("utf-8"))


class TestIPSRPCSetValueAction(DoorPiTestCase):

    @patch('doorpi.DoorPi', DoorPi)
    def test_instantiation(self):
        with self.assertRaises(ValueError):
            action.instantiate("set", "NaN", "something")

    @patch('doorpi.DoorPi', DoorPi)
    def test_action(self):
        ac = action.instantiate("set", 1, "somevalue")
        post = MagicMock(wraps=fake_post)
        with patch("requests.post", post):
            ac(EVENT_ID, EVENT_EXTRA)

        DoorPi().parse_string.assert_called_once_with("somevalue")


class TestIPSRPCCallFromVariableAction(DoorPiTestCase):

    @patch('doorpi.DoorPi', DoorPi)
    def test_instantiation(self):
        with self.assertRaises(ValueError):
            action.instantiate("call", "NaN")

    @patch('doorpi.DoorPi', DoorPi)
    def test_action(self):
        ac = action.instantiate("call", 1)
        post = MagicMock(wraps=fake_post)
        with patch("requests.post", post):
            ac(EVENT_ID, EVENT_EXTRA)

        DoorPi().sipphone.call.assert_called_once_with("**1")  # value set in fake_post above
