import logging
import pjsua2 as pj
import threading
import time

from . import logger
from .callbacks import AccountCallback, CallCallback
from .config import Config


class Worker():
    def __init__(self, sipphone):
        self.__phone = sipphone
        self.__ep = None

        self.running = True
        self.error = None
        self.ready = threading.Semaphore(0)
        self.wake = threading.Condition()

    def __call__(self):
        try: self.pjInit()
        except Exception as ex:
            self.error = ex
            return
        finally:
            self.ready.release()

        try:
            while self.running:
                e = self.__ep.libHandleEvents(0)
                if e < 0:
                    raise RuntimeError("Error while handling PJSUA2 native events: {msg} ({errno})"
                                       .format(errno=-e, msg=self.__ep.utilStrError(-e)))

                # Create any requested calls
                if len(self.__phone._Pjsua2__waiting_calls) > 0:
                    with self.__phone._Pjsua2__call_lock:
                        for uri in self.__phone._Pjsua2__waiting_calls:
                            call = CallCallback(self.__account)
                            callprm = pj.CallOpParam(True)
                            try: call.makeCall(uri, callprm)
                            except pj.Error as err:
                                logger.error("Error making a call: %s", err.info())
                                raise
                            self.__phone._Pjsua2__ringing_calls += [call]
                        self.__phone._Pjsua2__waiting_calls = []

                with self.wake: self.wake.wait(0.05)
        except Exception as ex:
            self.error = ex
            return

    def __del__(self):
        self.running = False
        self.__ep.libDestroy()

    def pjInit(self):
        """Initialize the PJSIP library. Called once by the worker thread."""
        logger.info("Initializing native library")
        self.__ep = pj.Endpoint()
        # N.B.: from PJSIP's perspective, the thread that calls
        # libCreate() is the main thread. Combined with
        # ``uaConfig.mainThreadOnly``, this ensures that all PJSIP
        # events will be handled here, and not by any native threads.
        self.__ep.libCreate()
        self.__ep.libInit(Config.endpoint_config())
        self.__ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, Config.transport_config())
        Config.setup_audio(self.__ep)
        self.__ep.libStart()

        logger.debug("Creating account")
        self.__account = AccountCallback()
        self.__account.create(Config.account_config())

        # Make sure the library can fully start up
        while True:
            e = self.__ep.libHandleEvents(20)  # note: libHandleEvents() takes milliseconds
            if e == 0: break
            if e < 0:
                raise RuntimeError("Error while initializing PJSUA2: {msg} ({errno})"
                                   .format(errno=-e, msg=self.__ep.utilStrError(-e)))
        logger.debug("Initialization complete")
