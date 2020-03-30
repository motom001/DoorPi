"""File I/O related stuff, i.e. the dial tone player and call recorder"""
# pylint: disable=protected-access, invalid-name

import logging

import pjsua2 as pj

import doorpi
from doorpi.actions import CallbackAction

LOGGER = logging.getLogger(__name__)


class DialTonePlayer:
    """Plays the dial tone while dialing."""

    def __init__(self, filename, loudness):
        self.__player = pj.AudioMediaPlayer()
        self.__target = None
        self.__level = loudness

        eh = doorpi.INSTANCE.event_handler
        ac_start = CallbackAction(self.start)
        ac_stop = CallbackAction(self.stop)

        eh.register_action("OnCallOutgoing_S", ac_start)
        eh.register_action("OnCallConnect_S", ac_stop)
        eh.register_action("OnCallDisconnect_S", ac_stop)
        eh.register_action("OnCallUnanswered_S", ac_stop)

        try:
            self.__player.createPlayer(str(filename))
        except pj.Error as err:
            LOGGER.error("Unable to create dial tone player: %s", err.info())
            self.__player = None

    def start(self):
        """Starts playing the dial tone."""
        if self.__player is None:
            LOGGER.error("Not playing dial tone due to previous errors")
            return

        if self.__target is None:
            self.__target = pj.Endpoint.instance().audDevManager().getPlaybackDevMedia()
        self.__player.startTransmit(self.__target)

    def stop(self):
        """Stops the dial tone."""
        if self.__player is None or self.__target is None: return

        self.__player.stopTransmit(self.__target)
        self.__player.setPos(0)
        self.__target = None


class CallRecorder:
    """Records calls."""

    def __init__(self, path, early, keep):
        self.__path = path
        self.__early = early
        self.__keep = keep

        self.__recorder = None

        eh = doorpi.INSTANCE.event_handler
        eh.register_action("OnCallOutgoing_S", CallbackAction(self.startEarly))
        eh.register_action("OnCallConnect_S", CallbackAction(self.start))
        eh.register_action("OnCallDisconnect_S", CallbackAction(self.stop))
        eh.register_action("OnCallDisconnect", CallbackAction(self.cleanup))
        if self.__path:
            LOGGER.debug("Call recording destination: %s", self.__path)

    def start(self):
        """Starts recording into a new file."""

        if self.__recorder is None:
            if not self.__path: return
            try:
                self.__path.mkdir(parents=True, exist_ok=True)
            except OSError:
                LOGGER.exception("Cannot create recording directory, unable to record call")
                return
            fname = self.__path / doorpi.INSTANCE.parse_string("recording_%Y-%m-%d_%H-%M-%S.wav")
            LOGGER.debug("Starting recording into file %s", fname)
            try:
                self.__recorder = pj.AudioMediaRecorder()
                self.__recorder.createRecorder(str(fname))
            except pj.Error as err:
                LOGGER.error("Unable to start recording: %s", err.info())
                self.__recorder = None
                return

            pj.Endpoint.instance().audDevManager().getCaptureDevMedia() \
                .startTransmit(self.__recorder)

        call = doorpi.INSTANCE.sipphone.current_call
        if call is not None:
            LOGGER.debug("Recording call to %s", repr(call.getInfo().remoteUri))
            call._CallCallback__getAudioVideoMedia()[0].startTransmit(self.__recorder)

    def startEarly(self):
        """Starts recording if configured to record early, i.e. while dialing."""

        if self.__early: self.start()

    def stop(self):
        """Stops an ongoing recording, if any."""

        if self.__recorder is not None:
            LOGGER.debug("Stopping call recorder")
            # N.B. For interpreters without refcounting semantics (e.g. PyPy),
            # delayed garbage collection may lead to additional data being recorded.
            self.__recorder = None

    def cleanup(self):
        """Clean up old recordings."""

        if not self.__path: return
        if self.__keep <= 0: return

        files = []
        try:
            with self.__path.iterdir() as it:
                files = [f for f in it
                         if f.name.startswith("recording_") and f.name.endswith(".wav")]
        except FileNotFoundError:
            LOGGER.warning("%s does not exist, skipping cleanup", self.__path)
        except OSError:
            LOGGER.exception("Unable to open %s for cleanup", self.__path)

        LOGGER.debug("%s holds %d recordings", self.__path, len(files))
        if len(files) <= self.__keep: return

        files.sort()
        for f in files[:-10]:
            LOGGER.info("Removing old recording %r", f.name)
            try:
                f.unlink()
            except FileNotFoundError:
                pass
            except OSError:
                LOGGER.exception("Cannot remove old recording %r", f.name)
