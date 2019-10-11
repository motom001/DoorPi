from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPi, DoorPiTestCase
from unittest.mock import patch

import doorpi.actions.http_request as action


class Namespace:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class TestHTTPRequestAction(DoorPiTestCase):

    def test_file_scheme(self):
        with self.assertRaises(ValueError, msg="file:// scheme must be invalid"):
            action.instantiate("file://localhost/tmp/test.txt")

    def test_ftp_scheme(self):
        with self.assertRaises(ValueError, msg="ftp:// scheme must be invalid"):
            action.instantiate("ftp://www.doorpi.org")

    def test_empty_domain(self):
        with self.assertRaises(ValueError, msg="Empty domain name must be invalid"):
            action.instantiate("http:///test.html")

    def test_empty_scheme(self):
        with self.assertRaises(ValueError, msg="Empty scheme must be invalid"):
            action.instantiate("://www.doorpi.org")

    @patch('requests.get')
    def test_action(self, req_get):
        req_get.return_value = Namespace(status_code=200, reason="OK")
        ac = action.instantiate("http://localhost/test.html")

        with self.assertLogs("doorpi.actions.http_request", "INFO"):
            ac(EVENT_ID, EVENT_EXTRA)
