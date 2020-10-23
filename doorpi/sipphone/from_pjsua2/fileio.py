"""File I/O related stuff, i.e. the dial tone player and call recorder"""
# pylint: disable=protected-access, invalid-name
import datetime
import gc
import logging
import pathlib
from importlib import resources
from typing import Optional, Union, cast

import pjsua2 as pj

import doorpi
import doorpi.sipphone.from_pjsua2.glue
from doorpi.actions import CallbackAction

LOGGER = logging.getLogger(__name__)


class DialTonePlayer:
    """Plays the dial tone while dialing."""

    __slots__ = ("_level", "_player", "_target")
    _player: Optional[pj.AudioMediaPlayer]
    _target: Optional[pj.AudioMedia]
    _level: float

    def __init__(
            self, filename: Union[str, pathlib.Path, None], loudness: float
            ) -> None:
        eh = doorpi.INSTANCE.event_handler

        if filename is None:
            ctx = resources.path(doorpi.sipphone, "dialtone.wav")
            eh.register_action(
                "OnShutdown", CallbackAction(
                    ctx.__exit__,  # pylint: disable=no-member
                    None, None, None))
            filename = ctx.__enter__()  # pylint: disable=no-member

        self._player = pj.AudioMediaPlayer()
        self._target = None
        self._level = loudness

        ac_start = CallbackAction(self.start)
        ac_stop = CallbackAction(self.stop)

        eh.register_action("OnCallOutgoing_S", ac_start)
        eh.register_action("OnCallConnect_S", ac_stop)
        eh.register_action("OnCallDisconnect_S", ac_stop)
        eh.register_action("OnCallUnanswered_S", ac_stop)

        try:
            self._player.createPlayer(str(filename))
        except pj.Error as err:
            LOGGER.error("Unable to create dial tone player: %s", err.info())
            self._player = None

    def start(self) -> None:
        """Start playing the dial tone"""
        if self._player is None:
            LOGGER.error("Not playing dial tone due to previous errors")
            return

        if self._target is None:
            self._target = (
                pj.Endpoint.instance().audDevManager().getPlaybackDevMedia())
        self._player.startTransmit(self._target)

    def stop(self) -> None:
        """Stop the dial tone"""
        if self._player is None or self._target is None:
            return

        self._player.stopTransmit(self._target)
        self._player.setPos(0)
        self._target = None


class CallRecorder:
    """Records calls"""
    def __init__(
            self, path: Optional[pathlib.Path], early: bool, keep: int,
            ) -> None:
        self.__path = path
        self.__early = early
        self.__keep = keep

        self.__recorder: Optional[pj.AudioMediaRecorder] = None

        eh = doorpi.INSTANCE.event_handler
        eh.register_action("OnCallOutgoing_S", CallbackAction(self.startEarly))
        eh.register_action("OnCallConnect_S", CallbackAction(self.start))
        eh.register_action("OnCallDisconnect_S", CallbackAction(self.stop))
        eh.register_action("OnCallDisconnect", CallbackAction(self.cleanup))
        if self.__path:
            LOGGER.debug("Call recording destination: %s", self.__path)

    def start(self) -> None:
        """Start recording into a new file"""
        if self.__recorder is None:
            if not self.__path:
                return
            try:
                self.__path.mkdir(parents=True, exist_ok=True)
            except OSError:
                LOGGER.exception(
                    "Cannot create recording directory, unable to record call")
                return
            fname = (
                self.__path / datetime.datetime.now().strftime(
                    "recording_%Y-%m-%d_%H-%M-%S.wav"))
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

        call = cast(
            doorpi.sipphone.from_pjsua2.glue.Pjsua2,
            doorpi.INSTANCE.sipphone,
        ).current_call
        if call is not None:
            LOGGER.debug("Recording call to %s", repr(call.getInfo().remoteUri))
            call._CallCallback__getAudioVideoMedia()[0] \
                .startTransmit(self.__recorder)

    def startEarly(self) -> None:
        """Start recording if configured to record while dialing"""
        if self.__early:
            self.start()

    def stop(self) -> None:
        """Stop an ongoing recording, if any"""
        if self.__recorder is not None:
            LOGGER.debug("Stopping call recorder")
            self.__recorder = None
            # Force garbage collection to stop recording now, even if
            # the current interpreter does not use refcounting
            gc.collect()

    def cleanup(self) -> None:
        """Clean up old recordings"""
        if not self.__path:
            return
        if self.__keep <= 0:
            return

        files = []
        try:
            files = [
                f for f in self.__path.iterdir()
                if f.name.startswith("recording_")
                and f.name.endswith(".wav")]
        except FileNotFoundError:
            LOGGER.warning("%s does not exist, skipping cleanup", self.__path)
        except OSError:
            LOGGER.exception("Unable to open %s for cleanup", self.__path)

        LOGGER.debug("%s holds %d recordings", self.__path, len(files))
        if len(files) <= self.__keep:
            return

        files.sort()
        for f in files[:-10]:
            LOGGER.info("Removing old recording %r", f.name)
            try:
                f.unlink()
            except FileNotFoundError:
                pass
            except OSError:
                LOGGER.exception("Cannot remove old recording %r", f.name)
