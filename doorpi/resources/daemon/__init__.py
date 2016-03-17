# -*- coding: utf-8 -*-

from main import DOORPI

logger = DOORPI.register_module(__name__, return_new_logger=True)


class DaemonRunnerStopFailureError(Exception): pass


class DaemonRunnerStartFailureError(Exception): pass


class DaemonRunnerInvalidActionError(Exception): pass


def load_daemon_libs():
    try:
        from daemon import runner
        from daemon.runner import DaemonRunnerInvalidActionError
        from daemon.runner import DaemonRunnerStartFailureError
        from daemon.runner import DaemonRunnerStopFailureError
        return True
    except ImportError:
        return False


DAEMON_AVAILABLE = load_daemon_libs()
