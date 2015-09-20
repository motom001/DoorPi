#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import datetime

from AbstractBaseClass import SipphoneAbstractBaseClass, SIPPHONE_SECTION
import linphone as lin

from doorpi import DoorPi
from doorpi.sipphone.linphone_lib.CallBacks import LinphoneCallbacks
from doorpi.sipphone.linphone_lib.Player import LinphonePlayer
from doorpi.sipphone.linphone_lib.Recorder import LinphoneRecorder
from doorpi.media.CreateDialTone import generate_dial_tone

conf = DoorPi().config

def log_handler(level, msg):
    if "pylinphone_Core_instance_method_iterate" in msg: return
    if "pylinphone_Core_get_current_call" in msg: return
    if "pylinphone_Call_from_native_ptr" in msg: return
    if ": keep alive sent to [" in msg: return
    method = getattr(logger, level)
    method(msg)

if logger.getEffectiveLevel() <= 5: lin.set_log_handler(log_handler)

def get(*args, **kwargs): return LinPhone(*args, **kwargs)
class LinPhone(SipphoneAbstractBaseClass):

    @property
    def name(self): return 'linphone wrapper'

    @property
    def lib(self): return self.__Lib
    @property
    def core(self): return self.__Lib

    @property
    def recorder(self): return self.__recorder
    __recorder = None

    @property
    def player(self): return self.__player
    __player = None

    @property
    def current_call(self): return self.core.current_call

    @property
    def video_devices(self):
        try:
            all_devices = []
            for video_device in self.core.video_devices:
                all_devices.append({
                  'name':       video_device
                })
            return all_devices
        except Exception:
            return []

    @property
    def sound_devices(self):
        try:
            all_devices = []
            for sound_device in self.core.sound_devices:
                all_devices.append({
                  'name':       sound_device,
                  'capture':    self.core.sound_device_can_capture(sound_device),
                  'record':     self.core.sound_device_can_playback(sound_device)
                })
            return all_devices
        except Exception as exp:
            logger.exception(exp)
            return []

    def _create_payload_enum(self, payloads):

        try:
            all_codecs = []
            for codec in payloads:
                all_codecs.append({
                    'name':         codec.mime_type,
                    'channels':     codec.channels,
                    'bitrate':      codec.normal_bitrate,
                    'enable':       self.core.payload_type_enabled(codec)
                })
            return all_codecs
        except Exception as exp:
            logger.exception(exp)
            return []

    @property
    def video_codecs(self):
        return self._create_payload_enum(self.core.video_codecs)

    @property
    def sound_codecs(self):
        return self._create_payload_enum(self.core.audio_codecs)

    @property
    def current_call_duration(self):
        if not self.current_call: return 0
        diff_start_and_now = datetime.datetime.utcnow() - self.__current_call_start_datetime
        return diff_start_and_now.total_seconds()

    @property
    def current_call_dump(self):
        try:
            return {
                'direction':        'incoming' if self.current_call.dir == 0 else 'outgoing',
                'remote_uri':       self.current_call.remote_address_as_string,
                'total_time':       self.current_call_duration,
                'level_incoming':   self.current_call.record_volume,
                'level_outgoing':   self.current_call.play_volume,
                'camera':           self.current_call.camera_enabled
            }
        except Exception:
            return {}

    #TODO: Datetime from linphone CallLog.start_date is more then 30 sec different to python datetime.utcnow()?
    __current_call_start_datetime = datetime.datetime.utcnow()

    @property
    def base_config(self):
        params = self.core.create_call_params(None)
        params.record_file = self.recorder.parsed_record_filename
        params.video_enabled = True
        return params

    def reset_call_start_datetime(self):
        self.__current_call_start_datetime = datetime.datetime.utcnow()
        logger.debug('reset current call start datetime to %s', self.__current_call_start_datetime)
        return self.__current_call_start_datetime

    def __init__(self, whitelist = list(), *args, **kwargs):
        logger.debug("__init__")

        DoorPi().event_handler.register_action('OnShutdown', self.destroy)

        DoorPi().event_handler.register_event('OnSipPhoneCreate', __name__)
        DoorPi().event_handler.register_event('OnSipPhoneStart', __name__)
        DoorPi().event_handler.register_event('OnSipPhoneDestroy', __name__)

        DoorPi().event_handler.register_event('OnSipPhoneRecorderCreate', __name__)
        DoorPi().event_handler.register_event('OnSipPhoneRecorderDestroy', __name__)

        DoorPi().event_handler.register_event('BeforeSipPhoneMakeCall', __name__)
        DoorPi().event_handler.register_event('OnSipPhoneMakeCall', __name__)
        DoorPi().event_handler.register_event('OnSipPhoneMakeCallFailed', __name__)
        DoorPi().event_handler.register_event('AfterSipPhoneMakeCall', __name__)
        
        DoorPi().event_handler.register_event('OnSipPhoneCallTimeoutNoResponse', __name__)
        DoorPi().event_handler.register_event('OnSipPhoneCallTimeoutMaxCalltime', __name__)

        DoorPi().event_handler.register_event('OnPlayerCreated', __name__)

        #http://pythonhosted.org/linphone/api_reference.html#linphone.Core.new
        self.callback = LinphoneCallbacks()
        config_path = None
        factory_config_path = None
        self.__Lib = lin.Core.new(
            self.callback.used_callbacks,
            config_path,
            factory_config_path
        )
        self.core.primary_contact = '%s <sip:doorpi@127.0.0.1>'%conf.get(SIPPHONE_SECTION, "identity", 'DoorPi')

    def start(self):
        DoorPi().event_handler('OnSipPhoneCreate', __name__)
        self.core.max_calls = conf.get_int(SIPPHONE_SECTION, 'ua.max_calls', 2)
        self.core.echo_cancellation_enabled = conf.get_bool(SIPPHONE_SECTION, 'echo_cancellation_enabled', False)
        
        # set local listen ports, default: random
        self.core.sip_transports = lin.SipTransports(conf.get_int(SIPPHONE_SECTION, 'local_port', 5060), conf.get_int(SIPPHONE_SECTION, 'local_port', 5060), -1, -1)

        self.core.video_display_enabled = conf.get_bool(SIPPHONE_SECTION, 'video_display_enabled', False)
        self.core.stun_server = conf.get(SIPPHONE_SECTION, 'stun_server', '')
        firewall_policy = conf.get(SIPPHONE_SECTION, 'FirewallPolicy', 'PolicyNoFirewall')
        if firewall_policy == "PolicyNoFirewall": self.core.firewall_policy = lin.FirewallPolicy.PolicyNoFirewall
        elif firewall_policy == "PolicyUseNatAddress": self.core.firewall_policy = lin.FirewallPolicy.PolicyUseNatAddress
        elif firewall_policy == "PolicyUseStun": self.core.firewall_policy = lin.FirewallPolicy.PolicyUseStun
        elif firewall_policy == "PolicyUseIce": self.core.firewall_policy = lin.FirewallPolicy.PolicyUseIce
        elif firewall_policy == "PolicyUseUpnp": self.core.firewall_policy = lin.FirewallPolicy.PolicyUseUpnp
        else: self.core.firewall_policy = lin.FirewallPolicy.PolicyNoFirewall

        #http://pythonhosted.org/linphone/api_reference.html#linphone.Core.in_call_timeout
        #After this timeout period, the call is automatically hangup.
        self.core.in_call_timeout = conf.get_int(SIPPHONE_SECTION, 'max_call_time', 120)
        #http://pythonhosted.org/linphone/api_reference.html#linphone.Core.inc_timeout
        #If an incoming call isn’t answered for this timeout period, it is automatically declined.
        self.core.inc_timeout = conf.get_int(SIPPHONE_SECTION, 'call_timeout', 15)

        self.__player = LinphonePlayer()
        self.core.ringback = self.player.player_filename
        self.__recorder = LinphoneRecorder()

        if len(self.core.sound_devices) == 0:
            logger.warning('no audio devices available')
        else:
            self.core.capture_device = conf.get(SIPPHONE_SECTION, 'capture_device', self.core.capture_device)
            self.core.playback_device = conf.get(SIPPHONE_SECTION, 'playback_device', self.core.playback_device)
            logger.info("found %s possible sounddevices:", len(self.core.sound_devices))
            logger.debug("|rec|play| name")
            logger.debug("------------------------------------")
            for sound_device in self.core.sound_devices:
                logger.debug("| %s | %s  | %s",
                    'X' if self.core.sound_device_can_capture(sound_device) else 'O',
                    'X' if self.core.sound_device_can_playback(sound_device) else 'O',
                    sound_device
                )
            logger.debug("------------------------------------")
            logger.debug("using capture_device: %s", self.core.capture_device)
            logger.debug("using playback_device: %s", self.core.playback_device)

        # Only enable PCMU and PCMA audio codecs by default
        config_audio_codecs = conf.get_list(SIPPHONE_SECTION, 'audio_codecs', 'PCMA,PCMU')
        for codec in self.core.audio_codecs:
            if codec.mime_type in config_audio_codecs:
                logger.debug('enable audio codec %s', codec.mime_type)
                self.core.enable_payload_type(codec, True)
            else:
                logger.debug('disable audio codec %s', codec.mime_type)
                self.core.enable_payload_type(codec, False)


        if len(self.core.video_devices) == 0:
            self.core.video_capture_enabled = False
            logger.warning('no video devices available')
        else:
            logger.info("found %s possible videodevices:", len(self.core.video_devices))
            logger.debug("| name")
            logger.debug("------------------------------------")
            for video_device in self.core.video_devices:
                logger.debug("| %s ", video_device)
            logger.debug("------------------------------------")
            config_camera = conf.get(SIPPHONE_SECTION, 'video_device', self.core.video_devices[0])
            if config_camera not in self.core.video_devices:
                logger.warning('camera "%s" from config does not exist in possible video devices.', config_camera)
                logger.debug('switching to first possible video device "%s"', self.core.video_devices[0])
                config_camera = self.core.video_devices[0]

            self.core.video_capture_enabled = True
            self.core.video_device = config_camera
            self.core.preferred_video_size_by_name = conf.get(SIPPHONE_SECTION, 'video_size', 'vga')
            logger.debug("using video_device: %s", self.core.video_device)

        # Only enable VP8 video codec
        config_video_codecs = conf.get_list(SIPPHONE_SECTION, 'video_codecs', 'VP8')
        for codec in self.core.video_codecs:
            if codec.mime_type in config_video_codecs and self.core.video_capture_enabled:
                logger.debug('enable video codec %s', codec.mime_type)
                self.core.enable_payload_type(codec, True)
            else:
                logger.debug('disable video codec %s', codec.mime_type)
                self.core.enable_payload_type(codec, False)

        # Configure the SIP account
        server = conf.get(SIPPHONE_SECTION, "sipserver_server")
        username = conf.get(SIPPHONE_SECTION, "sipserver_username")
        password = conf.get(SIPPHONE_SECTION, "sipserver_password", username)
        realm = conf.get(SIPPHONE_SECTION, "sipserver_realm", server)
        if server and username and password:
            logger.info('using DoorPi with SIP-Server')
            proxy_cfg = self.core.create_proxy_config()
            proxy_cfg.identity_address = lin.Address.new("%s <sip:%s@%s>" % (
                    conf.get(SIPPHONE_SECTION, "identity", 'DoorPi'), username, server)
            )
            proxy_cfg.server_addr = "sip:%s"%server
            proxy_cfg.register_enabled = True
            self.core.add_proxy_config(proxy_cfg)
            self.core.default_proxy_config = proxy_cfg
            auth_info = self.core.create_auth_info(username, None, password, None, None, realm)
            self.core.add_auth_info(auth_info)
        else:
            logger.info('using DoorPi without SIP-Server? Okay...')
            proxy_cfg = self.core.create_proxy_config()
            proxy_cfg.register_enabled = False
            self.core.add_proxy_config(proxy_cfg)
            self.core.default_proxy_config = proxy_cfg
            logger.debug('%s',self.core.proxy_config_list)

        logger.debug("start successfully")

    def destroy(self):
        logger.debug("destroy")
        self.core.terminate_all_calls()
        DoorPi().event_handler.fire_event_synchron('OnSipPhoneDestroy', __name__)
        DoorPi().event_handler.unregister_source(__name__, True)
        return

    def self_check(self, *args, **kwargs):
        if not self.core: return

        self.core.iterate()

        if not self.current_call: return

        if self.current_call.state < lin.CallState.Connected:
            if self.current_call_duration > self.core.inc_timeout - 0.5:
                logger.info("call timeout - hangup current call after %s seconds (max. %s)", self.current_call_duration, self.core.inc_timeout)
                self.core.terminate_all_calls()
                DoorPi().event_handler('OnSipPhoneCallTimeoutNoResponse', __name__)
        else:
            if int(self.current_call_duration) > self.core.in_call_timeout - 0.5:
                logger.info("max call time reached - hangup current call after %s seconds (max. %s)", self.current_call_duration, self.core.in_call_timeout)
                self.core.terminate_all_calls()
                DoorPi().event_handler('OnSipPhoneCallTimeoutMaxCalltime', __name__)

    def call(self, number):
        DoorPi().event_handler('BeforeSipPhoneMakeCall', __name__, {'number':number})
        logger.debug("call (%s)",str(number))
        if not self.current_call:
            logger.debug('no current call -> start new call')
            self.reset_call_start_datetime()
            if self.core.invite_with_params(number, self.base_config) is None:
                if DoorPi().event_handler.db.get_event_log_entries_count('OnSipPhoneMakeCallFailed') > 5:
                    logger.error('failed to execute call five times')
                else:
                    DoorPi().event_handler('OnSipPhoneMakeCallFailed', __name__, {'number':number})
                return None
            DoorPi().event_handler('OnSipPhoneMakeCall', __name__, {'number':number})
        elif number in self.current_call.remote_address.as_string_uri_only():
            if self.current_call_duration <= 2:
                logger.debug("same call %s again while call is running since %s seconds? -> skip",
                             self.core.current_call.remote_address.as_string_uri_only(),
                             self.current_call_duration
                )
            else:
                logger.debug("press twice with call duration > 1 second? Want to hangup current call? OK...")
                self.core.terminate_all_calls()
        else:
            logger.debug("new call needed? hangup old first...")
            self.core.terminate_all_calls()
            self.call(number)

        DoorPi().event_handler('AfterSipPhoneMakeCall', __name__, {'number':number})
        return self.current_call

    def is_admin_number(self, remote_uri):
        return self.callback.is_admin_number(remote_uri)

    def hangup(self):
        if self.current_call:
            logger.debug("Received hangup request, cancelling current call")
            self.core.terminate_call(self.current_call)
        else:
            logger.debug("Ignoring hangup request as there is no ongoing call")

