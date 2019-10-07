"""File I/O related stuff, i.e. the dial tone player and call recorder"""

import os
import pjsua2 as pj

from doorpi import DoorPi
from doorpi.actions import CallbackAction

from . import logger


class DialTonePlayer:
    def __init__(self, filename, loudness):
        self.__player = pj.AudioMediaPlayer()
        self.__target = None
        self.__level = loudness

        eh = DoorPi().event_handler
        ac_start = CallbackAction(self.start)
        ac_stop = CallbackAction(self.stop)

        eh.register_action("OnCallOutgoing_S", ac_start)
        eh.register_action("OnCallConnect_S", ac_stop)
        # Catch synthetic disconnects if no call was established
        eh.register_action("OnCallDisconnect_S", ac_stop)

        try: self.__player.createPlayer(filename)
        except pj.Error as err:
            logger.error("Unable to create dial tone player: %s", err.info())
            self.__player = None

    def start(self):
        if self.__player is None:
            logger.error("Not playing dial tone due to previous errors")
            return

        if self.__target is None:
            self.__target = pj.Endpoint.instance().audDevManager().getPlaybackDevMedia()
        self.__player.startTransmit(self.__target)

    def stop(self):
        if self.__player is None or self.__target is None: return

        self.__player.stopTransmit(self.__target)
        self.__player.setPos(0)
        self.__target = None


class CallRecorder:
    def __init__(self, path, early, keep):
        self.__path = path
        self.__early = early
        self.__keep = keep

        self.__recorder = None

        eh = DoorPi().event_handler
        eh.register_action("OnCallOutgoing_S", CallbackAction(self.startEarly))
        eh.register_action("OnCallConnect_S", CallbackAction(self.start))
        eh.register_action("OnCallDisconnect_S", CallbackAction(self.stop))
        eh.register_action("OnCallDisconnect", CallbackAction(self.cleanup))
        if self.__path:
            logger.debug("Call recording destination: %s", self.__path)

    def start(self):
        """Start recording"""

        if self.__recorder is None:
            if not self.__path: return
            try: os.makedirs(self.__path, exist_ok=True)
            except OSError:
                logger.exception("Cannot create recording directory, unable to record call")
                return
            fname = os.path.join(self.__path,
                                 DoorPi().parse_string("recording_%Y-%m-%d_%H-%M-%S.wav"))
            logger.debug("Starting recording into file %s", fname)
            try:
                self.__recorder = pj.AudioMediaRecorder()
                self.__recorder.createRecorder(fname)
            except pj.Error as err:
                logger.error("Unable to start recording: %s", err.info())
                self.__recorder = None
                return

            pj.Endpoint.instance().audDevManager().getCaptureDevMedia() \
                .startTransmit(self.__recorder)

        call = DoorPi().sipphone.current_call
        if call is not None:
            logger.debug("Recording call to %s", repr(call.getInfo().remoteUri))
            call._CallCallback__getAudioVideoMedia()[0].startTransmit(self.__recorder)

    def startEarly(self):
        """Start recording if configured to record early, i.e. while dialing."""

        if self.__early: self.start()

    def stop(self):
        """Stop recording."""

        if self.__recorder is not None:
            logger.debug("Stopping call recorder")
            self.__recorder = None

    def cleanup(self):
        """Clean up old recordings."""

        if not self.__path: return
        if self.__keep <= 0: return

        files = []
        try:
            with os.scandir(self.__path) as it:
                files = [f for f in it
                         if f.name.startswith("recording_") and f.name.endswith(".wav")]
        except FileNotFoundError:
            logger.warning("%s does not exist, skipping cleanup", self.__path)
        except OSError:
            logger.exception("Unable to open %s for cleanup", self.__path)

        logger.debug("%s holds %d recordings", self.__path, len(files))
        if len(files) <= self.__keep: return

        files.sort(key=lambda x: x.name)
        for f in files[:-10]:
            logger.info("Removing old recording %s", repr(f.name))
            try: os.remove(f.path)
            except FileNotFoundError: pass
            except OSError: logger.exception("Cannot remove old recording %s", f.name)
