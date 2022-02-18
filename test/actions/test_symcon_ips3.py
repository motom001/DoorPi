import io
import json
from unittest.mock import MagicMock, patch

from doorpi.actions import symcon_ips3

from ..mocks import DoorPi, DoorPiTestCase
from . import EVENT_EXTRA, EVENT_ID

stub_config = """\
[ip_symcon]
server = "localhost"
username = "root"
password = "root"
"""


class DummyResponse:
    def __init__(self, content):
        self.content = content


def fake_post(*args, data, **kw):
    del args, kw
    data = json.loads(data.decode("utf-8"))

    if data["method"] == "IPS_VariableExists":
        return DummyResponse(json.dumps({"result": True}).encode("utf-8"))
    if data["method"] == "IPS_GetVariable":
        return DummyResponse(
            json.dumps(
                {
                    "result": {
                        "VariableValue": {
                            "ValueType": symcon_ips3.IPSVariableType.STRING.value,
                        },
                    }
                }
            ).encode("utf-8")
        )
    if data["method"] == "GetValue":
        return DummyResponse(json.dumps({"result": "**1"}).encode("utf-8"))
    if data["method"] == "SetValue":
        return DummyResponse(json.dumps({"result": True}).encode("utf-8"))
    raise ValueError(f"Invalid method {data['method']!r}")


class TestIPSRPCSetValueAction(DoorPiTestCase):
    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_validation(self, instance):
        instance.config.load(io.StringIO(stub_config))
        with self.assertRaises(ValueError):
            symcon_ips3.instantiate("set", "NaN", "something")

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_action(self, instance):
        instance.config.load(io.StringIO(stub_config))
        ac = symcon_ips3.instantiate("set", 1, "somevalue")
        post = MagicMock(wraps=fake_post)
        with patch("requests.post", post):
            ac(EVENT_ID, EVENT_EXTRA)

        instance.parse_string.assert_called_once_with("somevalue")


class TestIPSRPCCallFromVariableAction(DoorPiTestCase):
    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_instantiation(self, instance):
        instance.config.load(io.StringIO(stub_config))
        with self.assertRaises(ValueError):
            symcon_ips3.instantiate("call", "NaN")

    @patch("doorpi.INSTANCE", new_callable=DoorPi)
    def test_action(self, instance):
        instance.config.load(io.StringIO(stub_config))
        ac = symcon_ips3.instantiate("call", 1)
        post = MagicMock(wraps=fake_post)
        with patch("requests.post", post):
            ac(EVENT_ID, EVENT_EXTRA)

        # value set in fake_post above
        instance.sipphone.call.assert_called_once_with("**1")
