import json
from unittest.mock import patch, MagicMock

from doorpi.actions import symcon_ips3

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase


class DummyResponse:
    def __init__(self, content):
        self.content = content


def fake_post(*args, data, **kw):
    del args, kw
    data = json.loads(data.decode("utf-8"))

    if data["method"] == "IPS_VariableExists":
        return DummyResponse(json.dumps({"result": True}).encode("utf-8"))
    if data["method"] == "IPS_GetVariable":
        return DummyResponse(json.dumps({"result": {
            "VariableValue": {
                "ValueType": symcon_ips3.IPSVariableType.STRING.value,
            },
        }}).encode("utf-8"))
    if data["method"] == "GetValue":
        return DummyResponse(json.dumps({"result": "**1"}).encode("utf-8"))
    if data["method"] == "SetValue":
        return DummyResponse(json.dumps({"result": True}).encode("utf-8"))
    raise ValueError(f"Invalid method {data['method']!r}")


class TestIPSRPCSetValueAction(DoorPiTestCase):

    @patch("doorpi.DoorPi", DoorPi)
    def test_validation(self):
        with self.assertRaises(ValueError):
            symcon_ips3.instantiate("set", "NaN", "something")

    @patch("doorpi.DoorPi", DoorPi)
    def test_action(self):
        ac = symcon_ips3.instantiate("set", 1, "somevalue")
        post = MagicMock(wraps=fake_post)
        with patch("requests.post", post):
            ac(EVENT_ID, EVENT_EXTRA)

        DoorPi().parse_string.assert_called_once_with("somevalue")


class TestIPSRPCCallFromVariableAction(DoorPiTestCase):

    @patch("doorpi.DoorPi", DoorPi)
    def test_instantiation(self):
        with self.assertRaises(ValueError):
            symcon_ips3.instantiate("call", "NaN")

    @patch("doorpi.DoorPi", DoorPi)
    def test_action(self):
        ac = symcon_ips3.instantiate("call", 1)
        post = MagicMock(wraps=fake_post)
        with patch("requests.post", post):
            ac(EVENT_ID, EVENT_EXTRA)

        DoorPi().sipphone.call.assert_called_once_with("**1")  # value set in fake_post above
