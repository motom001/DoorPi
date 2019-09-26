import logging
import os
import socket
import sys


logger = logging.getLogger(__name__)


class DoorPiSD:

    def __init__(self):
        self.sockaddr = None
        self.socket = None
        if "NOTIFY_SOCKET" in os.environ:
            logger.info("Enabling sd-notify protocol")
            self.sockaddr = os.environ["NOTIFY_SOCKET"]
            if self.sockaddr.startswith("@"):
                self.sockaddr[0] = "\0"

            # open notify socket
            try: self.socket = socket.socket(family=socket.AF_UNIX, type=socket.SOCK_DGRAM)
            except Exception as ex:
                logger.exception("Unable to open notification socket")
        else:
            logger.info("No NOTIFY_SOCKET in environment, sd-notify protocol disabled")

    def ready(self):
        """Tell the service manager that we are ready

        Inform the manager that service startup has completed
        successfully or that the service is done reloading its
        configuration.
        """
        return self.__send("READY=1")

    def reloading(self):
        """Tell the service manager that we are reloading configuration

        Inform the service manager that we have begun reloading our
        configuration files. Once done, `ready()` must be called again.
        """
        return self.__send("RELOADING=1")

    def stopping(self):
        """Tell the service manager that we are shutting down"""
        return self.__send("STOPPING=1")

    def status(self, msg):
        """Describe the service state for humans

        Passes a human readable, single-line status string back to the
        service manager that describes the current service state.
        """
        return self.__send("STATUS={}".format(msg.replace("\n", "\\n")))

    def watchdog(self):
        """Tell the service manager that we are still alive

        Tell the manager to update its watchdog timestamp. This is the
        keep-alive ping that a service needs to issue in regular
        intervals if WatchdogSec= is enabled for it.
        """
        return self.__send("WATCHDOG=1")

    def get_watchdog_timeout_usec(self):
        """Get the configured watchdog timeout

        Returns the configured watchdog timeout in microseconds. If
        `watchdog()` is not issued within that time after the last
        invocation, the service manager will fail this service. It is
        recommended that a daemon sends a keep-alive ping every half of
        the time returned here.

        If the watchdog logic is disabled for this service, or the
        corresponding environment variables were unset, this function
        will return None.
        """
        if "WATCHDOG_USEC" not in os.environ or os.environ["WATCHDOG_USEC"] == "0":
            return None  # no timeout given
        if "WATCHDOG_PID" in os.environ and os.environ["WATCHDOG_PID"] != str(os.getpid()):
            return None  # wrong PID
        return long(os.environ["WATCHDOG_USEC"])

    def __send(self, msg):
        """Actually send the messages to the daemon.
        This is used internally, and should not be called directly.
        """

        if self.socket is None or self.sockaddr is None:
            return
        try: self.socket.sendto(msg.encode("utf-8"), self.sockaddr)
        except Exception:
            logger.exception("Unable to send status information to service manager")
