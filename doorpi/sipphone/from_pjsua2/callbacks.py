import pjsua2 as pj

from doorpi import DoorPi
from doorpi.sipphone import SIPPHONE_SECTION

from . import fire_event, logger


class AccountCallback(pj.Account):

    def __init__(self):
        pj.Account.__init__(self)

    def onIncomingCall(self, iprm: pj.OnIncomingCallParam) -> None:
        sp = DoorPi().sipphone
        call = CallCallback(self, iprm.callId)
        callInfo = call.getInfo()
        oprm = pj.CallOpParam(False)
        event = None

        fire_event("BeforeCallIncoming", remote_uri=callInfo.remoteUri)

        try:
            if not sp.is_admin(callInfo.remoteUri):
                logger.info("Rejecting call from unregistered number %s", callInfo.remoteUri)
                oprm.statusCode = pj.PJSIP_SC_FORBIDDEN
                event = "OnCallReject"
                return

            with sp._Pjsua2__call_lock:
                if sp.current_call is not None and sp.current_call.isActive():
                    logger.info("Busy-rejecting call from %s", callInfo.remoteUri)
                    oprm.statusCode = pj.PJSIP_SC_BUSY_HERE
                    event = "OnCallBusy"
                    return
                else:
                    logger.info("Accepting incoming call from %s", callInfo.remoteUri)
                    oprm.statusCode = pj.PJSIP_SC_OK
                    event = "OnCallIncoming"
                    sp.current_call = call
                    return
        finally:
            call.answer(oprm)
            fire_event(event, remote_uri=callInfo.remoteUri)


class CallCallback(pj.Call):

    def __init__(self, acc: AccountCallback, callId=pj.PJSUA_INVALID_ID):
        logger.trace("Constructing call with callId %s", callId)
        super().__init__(acc, callId)

        self.__DTMF = ""
        self.__possible_DTMF = DoorPi().config.get_keys("DTMF")
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
        sp = DoorPi().sipphone
        eh = DoorPi().event_handler
        conf = DoorPi().config

        if ci.state == pj.PJSIP_INV_STATE_CALLING:
            logger.debug("Call to %s is now calling", repr(ci.remoteUri))
        elif ci.state == pj.PJSIP_INV_STATE_INCOMING:
            logger.debug("Call from %s is incoming", repr(ci.remoteUri))
        elif ci.state == pj.PJSIP_INV_STATE_EARLY:
            logger.debug("Call to %s is in early state", repr(ci.remoteUri))
        elif ci.state == pj.PJSIP_INV_STATE_CONNECTING:
            logger.debug("Call to %s is now connecting", repr(ci.remoteUri))
        elif ci.state == pj.PJSIP_INV_STATE_CONFIRMED:
            logger.info("Call to %s was accepted", repr(ci.remoteUri))
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
            logger.info("Call to %s disconnected after %d seconds (%d total)",
                        repr(ci.remoteUri), ci.connectDuration.sec, ci.totalDuration.sec)
            with sp._Pjsua2__call_lock:
                if sp.current_call == self:
                    sp.current_call = None
                elif self in sp._Pjsua2__ringing_calls:
                    sp._Pjsua2__ringing_calls.remove(self)

                if self.__fire_disconnect:
                    logger.trace("Firing disconnect event for call to %s", repr(ci.remoteUri))
                    fire_event("OnCallDisconnect", remote_uri=ci.remoteUri)
                elif len(sp._Pjsua2__ringing_calls) == 0:
                    logger.info("No call was answered")
                    fire_event("OnCallUnanswered")
                else: logger.trace("Skipping disconnect event for call to %s", repr(ci.remoteUri))
        else:
            logger.warning("Call to %s: unknown state %d", repr(ci.remoteUri), ci.state)

    def onCallMediaState(self, prm: pj.OnCallMediaStateParam) -> None:
        ci = self.getInfo()
        if ci.state != pj.PJSIP_INV_STATE_CONFIRMED:
            logger.debug("Ignoring media change in call to %s", repr(ci.remoteUri))
            return

        adm = pj.Endpoint.instance().audDevManager()
        logger.debug("Call to %s: media changed", repr(ci.remoteUri))
        audio, video = self.__getAudioVideoMedia()

        if audio:
            # Connect call audio to speaker and microphone
            audio.startTransmit(adm.getPlaybackDevMedia())
            adm.getCaptureDevMedia().startTransmit(audio)
            # Apply capture and ring tone loudness
            conf = DoorPi().config
            playback_loudness = conf.get_float(SIPPHONE_SECTION, "playback_loudness", 1.0)
            capture_loudness = conf.get_float(SIPPHONE_SECTION, "capture_loudness", 1.0)
            logger.trace("Adjusting RX level to %01.1f", playback_loudness)
            logger.trace("Adjusting TX level to %01.1f", capture_loudness)
            audio.adjustRxLevel(playback_loudness)
            audio.adjustTxLevel(capture_loudness)
        else: logger.error("Call to %s: no audio media", repr(ci.remoteUri))

    def onDtmfDigit(self, prm: pj.OnDtmfDigitParam) -> None:
        logger.debug("Received DTMF: %s", str(prm.digit))

        self.__DTMF += dg
        logger.trace("Processing digit %d; current sequence is %s", dg, self.__DTMF)

        prefix = False
        exact = False
        for dtmf in self.__possible_DTMF:
            if dtmf == self.__DTMF:
                exact = True
            elif dtmf.startswith(self.__DTMF):
                prefix = True

        if exact:
            remoteUri = self.getInfo().remoteUri
            fire_event(f"OnDTMF_{self.__DTMF}", async_only=True, remote_uri=remoteUri)
            self.dialDtmf("11")

        if not prefix:
            if not exact:
                self.dialDtmf("#")
            self.__DTMF = ""
