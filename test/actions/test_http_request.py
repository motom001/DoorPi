from unittest.mock import patch

from doorpi.actions import http_request

from . import EVENT_ID, EVENT_EXTRA
from ..mocks import DoorPiTestCase


class Namespace:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class TestHTTPRequestAction(DoorPiTestCase):

    def test_file_scheme(self):
        with self.assertRaises(ValueError, msg="file:// scheme must be invalid"):
            http_request.HTTPRequestAction("file://localhost/tmp/test.txt")

    def test_ftp_scheme(self):
        with self.assertRaises(ValueError, msg="ftp:// scheme must be invalid"):
            http_request.HTTPRequestAction("ftp://www.doorpi.org")

    def test_empty_domain(self):
        with self.assertRaises(ValueError, msg="Empty domain name must be invalid"):
            http_request.HTTPRequestAction("http:///test.html")

    def test_empty_scheme(self):
        with self.assertRaises(ValueError, msg="Empty scheme must be invalid"):
            http_request.HTTPRequestAction("://www.doorpi.org")

    @patch('requests.get')
    def test_action(self, req_get):
        req_get.return_value = Namespace(status_code=200, reason="OK")
        ac = http_request.HTTPRequestAction("http://localhost/test.html")

        with self.assertLogs("doorpi.actions.http_request", "INFO"):
            ac(EVENT_ID, EVENT_EXTRA)
