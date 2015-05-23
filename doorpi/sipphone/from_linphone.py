#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import datetime

from AbstractBaseClass import SipphoneAbstractBaseClass
import linphone as lin

from doorpi import DoorPi
from linphone_lib.CallBacks import LinphoneCallbacks
from linphone_lib.Player import LinphonePlayer
from linphone_lib.Recorder import LinphoneRecorder
from media.CreateDialTone import generate_dial_tone

SIPPHONE_SECTION = 'SIP-Phone'
conf = DoorPi().config

def log_handler(level, msg):
    if "pylinphone_Core_instance_method_iterate" in msg: return
    if "pylinphone_Core_get_current_call" in msg: return
    if "pylinphone_Call_from_native_ptr" in msg: return
    if ": keep alive sent to [" in msg: return
    method = getattr(logger, level)
    method(msg)

if logger.getEffectiveLevel() < 5: lin.set_log_handler(log_handler)

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
        except:
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
        except:
            return {}

    #TODO: Datetime from linphone CallLog.start_date is more then 30 sec different to python datetime.utcnow()?
    __current_call_start_datetime = datetime.datetime.utcnow()

    @property
    def base_config(self):
        params = self.core.create_call_params(None)
        params.record_file = self.recorder.parsed_record_filename
        return params

    def reset_call_start_datetime(self):
        self.__current_call_start_datetime = datetime.datetime.utcnow()
        logger.debug('reset current call start datetime to %s', self.__current_call_start_datetime)
        return self.__current_call_start_datetime

    def __init__(self, whitelist = [], *args, **kwargs):
        logger.debug("__init__")

        DoorPi().event_handler.register_action('OnShutdown', self.destroy)

        DoorPi().event_handler.register_event('OnSipPhoneCreate', __name__)
        DoorPi().event_handler.register_event('OnSipPhoneStart', __name__)
        DoorPi().event_handler.register_event('OnSipPhoneDestroy', __name__)

        DoorPi().event_handler.register_event('OnSipPhoneRecorderCreate', __name__)
        DoorPi().event_handler.register_event('OnSipPhoneRecorderDestroy', __name__)

        DoorPi().event_handler.register_event('OnSipPhoneMakeCall', __name__)
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
        self.core.inc_timeout = conf.get_int(SIPPHONE_SECTION, 'call_timeout', 45)

        self.core.capture_device = conf.get(SIPPHONE_SECTION, 'capture_device', '')
        self.core.playback_device = conf.get(SIPPHONE_SECTION, 'playback_device', '')

        self.__player = LinphonePlayer()
        self.core.ringback = self.player.player_filename

        self.__recorder = LinphoneRecorder()

        # e.g. 'V4L2: /dev/video0'
        camera = conf.get(SIPPHONE_SECTION, 'video_device', '')
        if len(camera):
            self.core.video_capture_enabled = True
            self.core.video_device = camera
            self.core.preferred_video_size_by_name = conf.get(SIPPHONE_SECTION, 'video_size', '')
        else:
            self.core.video_capture_enabled = False

        # Only enable PCMU and PCMA audio codecs
        for codec in self.core.audio_codecs:
            if codec.mime_type == "PCMA" or codec.mime_type == "PCMU":
                self.core.enable_payload_type(codec, True)
            else:
                self.core.enable_payload_type(codec, False)

        # Only enable VP8 video codec
        for codec in self.core.video_codecs:
            if codec.mime_type == "VP8" and len(camera):
                self.core.enable_payload_type(codec, True)
            else:
                self.core.enable_payload_type(codec, False)

        # Configure the SIP account
        server = conf.get(SIPPHONE_SECTION, "server")
        username = conf.get(SIPPHONE_SECTION, "username")
        password = conf.get(SIPPHONE_SECTION, "password", username)
        realm = conf.get(SIPPHONE_SECTION, "realm", server)
        if server and username and password:
            logger.info('using DoorPi with SIP-Server')
            proxy_cfg = self.core.create_proxy_config()
            proxy_cfg.identity = "%s <sip:%s@%s>"%(conf.get(SIPPHONE_SECTION, "identity", 'DoorPi'), username, server)
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

        DoorPi().event_handler.register_action(
            event_name      = 'OnTimeTickRealtime',
            action_object   = 'pjsip_handle_events:50'
        )

        logger.debug("start successfully")
        logger.debug("founded %s possible sounddevices:", len(self.core.sound_devices))
        logger.debug("|rec|play| name")
        logger.debug("------------------------------------")
        for sound_device in self.core.sound_devices:
            logger.debug("| %s | %s  | %s",
                'X' if self.core.sound_device_can_capture(sound_device) else 'O',
                'X' if self.core.sound_device_can_playback(sound_device) else 'O',
                sound_device
            )
        logger.debug("------------------------------------")
        logger.debug("used capture_device: %s", self.core.capture_device)
        logger.debug("used playback_device: %s", self.core.playback_device)

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
        logger.debug("call (%s)",str(number))
        if not self.current_call:
            logger.debug('no current call -> start new call')
            self.reset_call_start_datetime()
            self.core.invite_with_params(number, self.base_config)
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
