import logging
import pjsua2 as pj

from doorpi import DoorPi
from doorpi.sipphone import DEFAULT_MEDIA_DIR, SIPPHONE_SECTION

from . import logger


conf = DoorPi().config


class Config:
    @staticmethod
    def call_timeout() -> int:
        return conf.get_int(SIPPHONE_SECTION, "call_timeout", 15)

    @staticmethod
    def max_call_time() -> int:
        return conf.get_int(SIPPHONE_SECTION, "max_call_time", 120)

    @staticmethod
    def sipphone_server() -> str:
        return conf.get_string(SIPPHONE_SECTION, "sipserver_server")

    @staticmethod
    def account_config() -> pj.AccountConfig:
        logger.trace("Creating account config")
        acfg = pj.AccountConfig()
        identity = conf.get_string(SIPPHONE_SECTION, "identity", "DoorPi")
        sip_server = Config.sipphone_server()
        sip_user = conf.get_string(SIPPHONE_SECTION, "sipserver_username")
        sip_pass = conf.get_string(SIPPHONE_SECTION, "sipserver_password", password=True)
        sip_realm = conf.get_string(SIPPHONE_SECTION, "sipserver_realm", sip_server)
        if not sip_user: raise ValueError(f"No username given in [{SIPPHONE_SECTION}]")
        if not sip_server: raise ValueError(f"No server given in [{SIPPHONE_SECTION}]")

        if identity:
            identity = identity.replace("\\", "\\\\").replace("\"", "\\\"")
            acfg.idUri = f"\"{identity}\" <sip:{sip_user}@{sip_server}>"
        else:
            acfg.idUri = f"sip:{sip_user}@{sip_server}"

        acfg.regConfig.registrarUri = f"sip:{sip_server}"
        acfg.regConfig.registerOnAdd = True

        authCred = pj.AuthCredInfo()
        authCred.scheme = "digest"
        authCred.realm = sip_realm
        authCred.username = sip_user
        authCred.dataType = 0  # plain text password
        authCred.data = sip_pass
        acfg.sipConfig.authCreds.append(authCred)

        acfg.presConfig.publishEnabled = True
        return acfg

    @staticmethod
    def dialtone_config() -> dict:
        conf = DoorPi().config
        return {
            "filename": conf.get_string_parsed(SIPPHONE_SECTION, "dialtone",
                                               f"{DEFAULT_MEDIA_DIR}/dialtone.wav"),
            "loudness": conf.get_float(SIPPHONE_SECTION, "dialtone_loudness", 1.0)
        }

    @staticmethod
    def endpoint_config() -> pj.EpConfig:
        logger.trace("Creating endpoint config")
        ep_cfg = pj.EpConfig()
        ep_cfg.uaConfig.maxCalls = conf.get_int(SIPPHONE_SECTION, "max_calls", 8)
        stun_server = conf.get_string(SIPPHONE_SECTION, "stun_server", "")
        if stun_server:
            ep_cfg.uaConfig.stunServer.append(stun_server)
        # Ensure PJSIP callbacks will be handled by our python worker thread
        ep_cfg.uaConfig.threadCnt = 0
        ep_cfg.uaConfig.mainThreadOnly = True

        ep_cfg.logConfig.msgLogging = False  # Don't log full SIP messages
        ep_cfg.logConfig.level = 5
        ep_cfg.logConfig.consoleLevel = 4
        ep_cfg.logConfig.decor = False

        logwriter = DoorPiLogWriter(logger.getChild("native"))
        ep_cfg.logConfig.writer = logwriter
        # Bind the LogWriter's lifetime to the sipphone object, so that
        # it won't be garbage-collected prematurely.
        DoorPi().sipphone.__logwriter = logwriter

        return ep_cfg

    @staticmethod
    def recorder_config() -> dict:
        conf = DoorPi().config
        return {
            "path": conf.get_string_parsed(SIPPHONE_SECTION, "record_path", ""),
            "early": conf.get_bool(SIPPHONE_SECTION, "record_while_dialing", True),
            "keep": conf.get_int(SIPPHONE_SECTION, "record_keep", 10),
        }

    @staticmethod
    def transport_config() -> pj.TransportConfig:
        logger.trace("Creating transport config")
        t_cfg = pj.TransportConfig()
        t_cfg.port = conf.get_int(SIPPHONE_SECTION, "local_port", 0)
        return t_cfg

    @staticmethod
    def list_audio_devices(adm: pj.AudDevManager, loglevel: int) -> None:
        if not logger.isEnabledFor(loglevel): return
        devs = adm.enumDev()
        for i in range(len(devs)):
            logger.log(loglevel, f"   {devs[i].driver}:{devs[i].name}")

    @classmethod
    def setup_audio(cls, ep: pj.Endpoint) -> None:
        logger.trace("Setting up audio on %s", repr(ep))
        adm = ep.audDevManager()
        cls.setup_audio_devices(adm)
        cls.setup_audio_volume(adm)
        cls.setup_audio_codecs(ep)
        cls.setup_audio_echo_cancellation(adm)

    @classmethod
    def setup_audio_devices(cls, adm: pj.AudDevManager) -> None:
        logger.trace("PJSUA2 found %d audio devices", adm.getDevCount())
        if adm.getDevCount() == 0:
            raise RuntimeError("No audio devices found by PJSUA2")

        # Setup configured capture / playback devices
        capture_device = conf.get_string(SIPPHONE_SECTION, "capture_device")
        playback_device = conf.get_string(SIPPHONE_SECTION, "playback_device")
        audio_devices = adm.enumDev()
        if capture_device == "" or playback_device == "":
            logger.critical("No audio devices configured! Detected audio devices:")
            cls.list_audio_devices(adm, logging.CRITICAL)
            raise ValueError("No audio devices configured (See log for possible options)")

        capture_drv = capture_device.split(":")[0]
        # The split-rejoin is necessary to handle device names with ":"
        capture_dev = ":".join(capture_device.split(":")[1:])
        playback_drv = playback_device.split(":")[0]
        playback_dev = ":".join(playback_device.split(":")[1:])
        try: capture_idx = adm.lookupDev(capture_drv, capture_dev)
        except pj.Error:
            logger.critical("Configured capture device not found! Found devices:")
            cls.list_audio_devices(adm, logging.CRITICAL)
            raise ValueError(f"Configured capture device could not be found: {capture_device}")
        try: playback_idx = adm.lookupDev(playback_drv, playback_dev)
        except pj.Error:
            logger.critical("Configured playback device not found! Found devices:")
            cls.list_audio_devices(adm, logging.CRITICAL)
            raise ValueError(f"Configured playback device could not be found: {playback_device}")
        logger.trace("Device indices: capture = %d, playback = %d", capture_idx, playback_idx)
        adm.setCaptureDev(capture_idx)
        adm.setPlaybackDev(playback_idx)

    @staticmethod
    def setup_audio_volume(adm: pj.AudDevManager) -> None:
        capture_volume = conf.get_int(SIPPHONE_SECTION, "capture_volume", 100)
        playback_volume = conf.get_int(SIPPHONE_SECTION, "playback_volume", 100)
        if playback_volume >= 0:
            logger.trace("Setting playback volume to %d", playback_volume)
            try: adm.setOutputVolume(playback_volume, True)
            except pj.Error as err:
                logger.error("Unable to set playback volume "
                             "(Set playback_volume to -1 to silence this error)\n%s", err.info())
        if capture_volume >= 0:
            logger.trace("Setting capture volume to %d", playback_volume)
            try: adm.setInputVolume(capture_volume, True)
            except pj.Error as err:
                logger.error("Unable to set capture volume "
                             "(Set capture_volume to -1 to silence this error)\n%s", err.info())

    @staticmethod
    def setup_audio_codecs(ep: pj.Endpoint) -> None:
        allcodecs = ep.codecEnum()
        logger.debug("Supported audio codecs: %s", ", ".join([c.codecId for c in allcodecs]))
        confcodecs = conf.get_string(SIPPHONE_SECTION, "audio_codecs", "opus, PCMA, PCMU")
        if not confcodecs: return

        confcodecs = [c.strip().lower() for c in confcodecs.split(",")]
        for c in allcodecs:
            # In PJSIP, codecs follow the format "codec/samplerate/num".
            # Since the same codec can exist multiple times with
            # different sample rate, we need to check each part of the
            # codec ID individually.
            ci = c.codecId.lower()
            cn, cs, cm = ci.split("/")
            p = 0
            for match in [ci, "/".join([cn, cs]), cn]:
                i = None
                try: i = confcodecs.index(match)
                except ValueError: continue
                p = 255 - i  # 255 = highest priority
                break
            logger.trace("Changing priority of codec %s from %d to %d", c.codecId, c.priority, p)
            ep.codecSetPriority(c.codecId, p)

    @staticmethod
    def setup_audio_echo_cancellation(adm: pj.AudDevManager) -> None:
        if conf.get_boolean(SIPPHONE_SECTION, "echo_cancellation_enabled", False):
            tail = conf.get_int(SIPPHONE_SECTION, "echo_cancellation_tail", 250)
            logger.trace("Setting echo cancellation tail length to %dms", tail)
            adm.setEcOptions(tail, 0)
        else:
            logger.trace("Disabling echo cancellation")
            adm.setEcOptions(0, 0)


class DoorPiLogWriter(pj.LogWriter):
    def __init__(self, logger):
        super().__init__()
        self.__logger = logger

    def write(self, e):
        if e.level <= 1: self.__logger.error("%s", e.msg)
        elif e.level <= 2: self.__logger.warning("%s", e.msg)
        elif e.level <= 3: self.__logger.info("%s", e.msg)
        elif e.level <= 4: self.__logger.debug("%s", e.msg)
        else: self.__logger.trace("[level %d] %s", e.level, e.msg)
