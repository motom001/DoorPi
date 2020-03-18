import os
import socket
from unittest.mock import patch

from doorpi.status.systemd import DoorPiSD

from ..mocks import DoorPiTestCase


SOCKET_PATH = "/tmp/doorpi_test_sdnotify"

ABSTRACT_SOCKET_PATH = "@sdnotify"
EXPECTED_ABSTRACT_SOCKET_PATH = "\0sdnotify"


class TestDoorPiSDInactive(DoorPiTestCase):

    def setUp(self):
        super().setUp()
        # Make sure the environment is clean
        for i in ("NOTIFY_SOCKET", "WATCHDOG_USEC", "WATCHDOG_PID"):
            if i in os.environ:
                del os.environ[i]

    @patch("socket.socket")
    def test_ready(self, mocksock):
        with self.assertLogs("doorpi.status.systemd", "INFO"):
            dpsd = DoorPiSD()
        mocksock.assert_not_called()
        self.assertIsNone(dpsd.socket)
        self.assertIsNone(dpsd.sockaddr)

        dpsd.ready()

    @patch("socket.socket")
    def test_watchdog(self, mocksock):
        del mocksock
        with self.assertLogs("doorpi.status.systemd", "INFO"):
            dpsd = DoorPiSD()

        self.assertIsNone(dpsd.get_watchdog_timeout_usec())


class TestDoorPiSD(DoorPiTestCase):

    def setUp(self):
        super().setUp()
        os.environ["WATCHDOG_USEC"] = str(4_000_000)
        os.environ["WATCHDOG_PID"] = str(os.getpid())
        os.environ["NOTIFY_SOCKET"] = SOCKET_PATH
        self.expected_socket_path = SOCKET_PATH

    def tearDown(self):
        super().tearDown()
        del os.environ["NOTIFY_SOCKET"]

    @patch("socket.socket")
    def test_watchdog(self, mocksock):
        del mocksock
        with self.assertLogs("doorpi.status.systemd", "INFO"):
            dpsd = DoorPiSD()

        self.assertEqual(dpsd.get_watchdog_timeout_usec(), 4_000_000)

    @patch("socket.socket")
    def test_messages(self, mocksock):
        with self.assertLogs("doorpi.status.systemd", "INFO"):
            dpsd = DoorPiSD()

        mocksock.assert_called_once_with(family=socket.AF_UNIX, type=socket.SOCK_DGRAM)

        dpsd.ready()
        dpsd.reloading()
        dpsd.stopping()
        dpsd.status("\U0001F408\n")
        dpsd.watchdog()

        self.assertEqual(mocksock().sendto.call_args_list, [
            ((b"READY=1", self.expected_socket_path),),
            ((b"RELOADING=1", self.expected_socket_path),),
            ((b"STOPPING=1", self.expected_socket_path),),
            ((b"STATUS=" + "\U0001F408".encode("utf-8") + br"\n", self.expected_socket_path),),
            ((b"WATCHDOG=1", self.expected_socket_path),),
        ])


class TestDoorPiSDAbstractSocketNamespace(TestDoorPiSD):

    def setUp(self):
        super().setUp()
        os.environ["NOTIFY_SOCKET"] = ABSTRACT_SOCKET_PATH
        self.expected_socket_path = EXPECTED_ABSTRACT_SOCKET_PATH
