"""Callbacks from the native library."""
# pylint: disable=protected-access, invalid-name

import logging

import pjsua2 as pj

import doorpi

from . import fire_event

LOGGER = logging.getLogger(__name__)


class AccountCallback(pj.Account):

    def __init__(self):
        pj.Account.__init__(self)

    # pylint: disable=arguments-differ
    def onIncomingCall(self, iprm: pj.OnIncomingCallParam) -> None:
        sp = doorpi.INSTANCE.sipphone
        call = CallCallback(self, iprm.callId)
        callInfo = call.getInfo()
        oprm = pj.CallOpParam(False)
        event = None

        fire_event("BeforeCallIncoming", remote_uri=callInfo.remoteUri)

        try:
            if not sp.is_admin(callInfo.remoteUri):
                LOGGER.info("Rejecting call from unregistered number %s", callInfo.remoteUri)
                oprm.statusCode = pj.PJSIP_SC_FORBIDDEN
                event = "OnCallReject"
                return

            with sp._Pjsua2__call_lock:
                if sp.current_call is not None and sp.current_call.isActive():
                    LOGGER.info("Busy-rejecting call from %s", callInfo.remoteUri)
                    oprm.statusCode = pj.PJSIP_SC_BUSY_HERE
                    event = "OnCallBusy"
                else:
                    LOGGER.info("Accepting incoming call from %s", callInfo.remoteUri)
                    oprm.statusCode = pj.PJSIP_SC_OK
                    event = "OnCallIncoming"
                    sp.current_call = call
        finally:
            call.answer(oprm)
            fire_event(event, remote_uri=callInfo.remoteUri)


class CallCallback(pj.Call):

    def __init__(self, acc: AccountCallback, callId=pj.PJSUA_INVALID_ID):
        LOGGER.trace("Constructing call with callId %s", callId)
        super().__init__(acc, callId)

        self.__dtmf = ""
        self.__possible_dtmf = (
            doorpi.INSTANCE.config.view("sipphone.dtmf").keys())
        self.__fire_disconnect = False

    def __getAudioVideoMedia(self):
        """Helper function that returns the first audio and video media"""

        audio = None
        video = None
        ci = self.getInfo()
        for i in range(len(ci.media)):
            if ci.media[i].type == pj.PJMEDIA_TYPE_AUDIO and audio is None:
                audio = pj.AudioMedia.typecastFromMedia(self.getMedia(i))
            if ci.media[i].type == pj.PJMEDIA_TYPE_VIDEO and video is None:
                video = pj.AudioMedia.typecastFromMedia(self.getMedia(i))
        return (audio, video)

    def onCallState(self, prm: pj.OnCallStateParam) -> None:
        ci = self.getInfo()
        sp = doorpi.INSTANCE.sipphone

        if ci.state == pj.PJSIP_INV_STATE_CALLING:
            LOGGER.debug("Call to %r is now calling", ci.remoteUri)
        elif ci.state == pj.PJSIP_INV_STATE_INCOMING:
            LOGGER.debug("Call from %r is coming in", ci.remoteUri)
        elif ci.state == pj.PJSIP_INV_STATE_EARLY:
            LOGGER.debug("Call to %r is in early state", ci.remoteUri)
        elif ci.state == pj.PJSIP_INV_STATE_CONNECTING:
            LOGGER.debug("Call to %r is now connecting", ci.remoteUri)
        elif ci.state == pj.PJSIP_INV_STATE_CONFIRMED:
            LOGGER.info("Call to %r was accepted", ci.remoteUri)
            self.__fire_disconnect = True
            with sp._Pjsua2__call_lock:
                prm = pj.CallOpParam()
                if sp.current_call is not None:
                    # (note: this should not be possible)
                    sp.current_call.hangup(prm)
                    sp.current_call = None

                sp.current_call = self
                for ring in sp._Pjsua2__ringing_calls:
                    if self != ring: ring.hangup(prm)
                sp._Pjsua2__ringing_calls = []
                sp._Pjsua2__waiting_calls = []
                fire_event("OnCallConnect", remote_uri=ci.remoteUri)
        elif ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
            LOGGER.info("Call to %r disconnected after %d seconds (%d total)",
                        ci.remoteUri, ci.connectDuration.sec, ci.totalDuration.sec)
            with sp._Pjsua2__call_lock:
                if sp.current_call == self:
                    sp.current_call = None
                elif self in sp._Pjsua2__ringing_calls:
                    sp._Pjsua2__ringing_calls.remove(self)

                if self.__fire_disconnect:
                    LOGGER.trace("Firing disconnect event for call to %r", ci.remoteUri)
                    fire_event("OnCallDisconnect", remote_uri=ci.remoteUri)
                elif len(sp._Pjsua2__ringing_calls) == 0:
                    LOGGER.info("No call was answered")
                    fire_event("OnCallUnanswered")
                else: LOGGER.trace("Skipping disconnect event for call to %r", ci.remoteUri)
        else:
            LOGGER.warning("Call to %r: unknown state %d", ci.remoteUri, ci.state)

    def onCallMediaState(self, prm: pj.OnCallMediaStateParam) -> None:
        ci = self.getInfo()
        if ci.state != pj.PJSIP_INV_STATE_CONFIRMED:
            LOGGER.debug("Ignoring media change in call to %r", ci.remoteUri)
            return

        adm = pj.Endpoint.instance().audDevManager()
        LOGGER.debug("Call to %r: media changed", ci.remoteUri)
        audio, _ = self.__getAudioVideoMedia()

        if audio:
            # Connect call audio to speaker and microphone
            audio.startTransmit(adm.getPlaybackDevMedia())
            adm.getCaptureDevMedia().startTransmit(audio)
            # Apply capture and ring tone loudness
            conf = doorpi.INSTANCE.config
            playback_loudness = conf["sipphone.playback.loudness"]
            capture_loudness = conf["sipphone.capture.loudness"]
            LOGGER.trace("Adjusting RX level to %01.1f", playback_loudness)
            LOGGER.trace("Adjusting TX level to %01.1f", capture_loudness)
            audio.adjustRxLevel(playback_loudness)
            audio.adjustTxLevel(capture_loudness)
        else: LOGGER.error("Call to %r: no audio media", ci.remoteUri)

    def onDtmfDigit(self, prm: pj.OnDtmfDigitParam) -> None:
        LOGGER.debug("Received DTMF: %s", prm.digit)

        self.__dtmf += prm.digit
        LOGGER.trace("Processing digit %s; current sequence is %s", prm.digit, self.__dtmf)

        prefix = False
        exact = False
        for dtmf in self.__possible_dtmf:
            if dtmf == self.__dtmf:
                exact = True
            elif dtmf.startswith(self.__dtmf):
                prefix = True

        if exact:
            remoteUri = self.getInfo().remoteUri
            fire_event(f"OnDTMF_{self.__dtmf}", async_only=True, remote_uri=remoteUri)
            self.dialDtmf("11")

        if not prefix:
            if not exact:
                self.dialDtmf("#")
            self.__dtmf = ""
