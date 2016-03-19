#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import pjsua as pj

from time import sleep

from doorpi.sipphone.pjsua_lib.Config import *
from doorpi.sipphone.pjsua_lib.SipPhoneAccountCallBack import SipPhoneAccountCallBack
from doorpi.sipphone.pjsua_lib.SipPhoneCallCallBack import SipPhoneCallCallBack
from doorpi.sipphone.pjsua_lib.Recorder import PjsuaRecorder
from doorpi.sipphone.pjsua_lib.Player import PjsuaPlayer
from AbstractBaseClass import SipphoneAbstractBaseClass

from doorpi import DoorPi

def get(*args, **kwargs): return Pjsua()
class Pjsua(SipphoneAbstractBaseClass):

    @property
    def name(self): return 'PJSUA wrapper'

    @property
    def lib(self): return self.__Lib

    @property
    def recorder(self): return self.__recorder

    @property
    def player(self): return self.__player

    @property
    def sound_devices(self):
        try:
            all_devices = []
            for sound_device in self.lib.enum_snd_dev():
                all_devices.append({
                  'name':       sound_device,
                  'capture':    True if sound_device.input_channels > 0 else False,
                  'record':     True if sound_device.output_channels > 0 else False
                })
            return all_devices
        except: return []

    @property
    def sound_codecs(self):
        try:
            all_codecs = []
            for codec in self.lib.enum_codecs():
                all_codecs.append({
                    'name':         codec.name,
                    'channels':     codec.channel_count,
                    'bitrate':      codec.avg_bps
                })
        except: return []

    @property
    def current_call_dump(self):
        try:
            return {
                'direction':        'incoming' if self.current_call.info().role == 0 else 'outgoing',
                'remote_uri':       self.current_call.info().remote_uri,
                'total_time':       self.current_call.info().call_time,
                'level_incoming':   self.lib.conf_get_signal_level(0)[0],
                'level_outgoing':   self.lib.conf_get_signal_level(0)[1],
                'camera':           False
            }
        except:
            return {}

    def thread_register(self, name): return self.lib.thread_register(name)

    def __init__(self, *args, **kwargs):
        logger.debug("__init__")

        DoorPi().event_handler.register_event('OnSipPhoneCreate', __name__)
        DoorPi().event_handler.register_event('OnSipPhoneStart', __name__)
        DoorPi().event_handler.register_event('OnSipPhoneDestroy', __name__)

        DoorPi().event_handler.register_event('OnSipPhoneRecorderCreate', __name__)
        DoorPi().event_handler.register_event('OnSipPhoneRecorderDestroy', __name__)

        DoorPi().event_handler.register_event('BeforeSipPhoneMakeCall', __name__)
        DoorPi().event_handler.register_event('OnSipPhoneMakeCall', __name__)
        DoorPi().event_handler.register_event('AfterSipPhoneMakeCall', __name__)
        
        DoorPi().event_handler.register_event('OnSipPhoneCallTimeoutNoResponse', __name__)
        DoorPi().event_handler.register_event('OnSipPhoneCallTimeoutMaxCalltime', __name__)

        self.__Lib = None
        self.__account = None
        self.current_callcallback = None
        self.current_account_callback = None
        self.__recorder = None
        self.__player = None

        self.call_timeout = 30

    def start(self):
        DoorPi().event_handler('OnSipPhoneCreate', __name__)
        self.__Lib = pj.Lib.instance()
        if self.__Lib is None: self.__Lib = pj.Lib()

        logger.debug("init Lib")
        self.__Lib.init(
            ua_cfg      = doorpi.sipphone.pjsua_lib.Config.create_UAConfig(),
            media_cfg   = doorpi.sipphone.pjsua_lib.Config.create_MediaConfig(),
            log_cfg     = doorpi.sipphone.pjsua_lib.Config.create_LogConfig()
        )

        logger.debug("init transport")
        transport = self.__Lib.create_transport(
            type        = pj.TransportType.UDP,
            cfg         = doorpi.sipphone.pjsua_lib.Config.create_TransportConfig()
        )
        logger.debug("Listening on: %s",str(transport.info().host))
        logger.debug("Port: %s",str(transport.info().port))

        logger.debug("Lib.start()")
        self.lib.start(0)

        DoorPi().event_handler.register_action(
            event_name      = 'OnTimeTick',
            action_object   = 'pjsip_handle_events:50'
        )

        logger.debug("init Acc")
        self.current_account_callback = SipPhoneAccountCallBack()
        self.__account = self.__Lib.create_account(
            acc_config  = doorpi.sipphone.pjsua_lib.Config.create_AccountConfig(),
            set_default = True,
            cb          = self.current_account_callback
        )

        self.call_timeout = doorpi.sipphone.pjsua_lib.Config.call_timeout()
        self.max_call_time = doorpi.sipphone.pjsua_lib.Config.max_call_time()

        DoorPi().event_handler('OnSipPhoneStart', __name__)

        self.__recorder = PjsuaRecorder()
        self.__player = PjsuaPlayer()

        logger.debug("start successfully")

    def stop(self, timeout = -1):
        if self.current_call is None:
            logger.debug('no call? -> nothing to do to clean up')
            return True
        else:
            call_info = self.current_call.info()
            if call_info.total_time > timeout:
                logger.info('call timeout - call.info().total_time %s', call_info.total_time)
                return self.hangup()
            return True

    def destroy(self):
        logger.debug("destroy")
        DoorPi().event_handler('OnSipPhoneDestroy', __name__)

        if self.lib is not None:
            self.lib.handle_events()
            self.__Lib.destroy()
            self.lib.handle_events()

        try:
            timeout = 0
            while timeout < 5 and self.__Lib is not None:
                sleep(0.1)
                timeout += 0.1
                self.lib.handle_events()

        except:
            DoorPi().event_handler.unregister_source(__name__, True)
            return

    def self_check(self, timeout):
        self.lib.thread_register('pjsip_handle_events')

        self.lib.handle_events(timeout)

        if self.current_call is not None:
            if self.current_call.is_valid() is 0:
                del self.current_callcallback
                self.current_callcallback = None
                del self.current_call
                self.current_call = None

            try:
                if self.current_call.info().call_time == 0 \
                and self.current_call.info().total_time > self.call_timeout:
                    logger.info("call timeout - hangup current call after %s seconds", self.call_timeout)
                    self.current_call.hangup()
                    DoorPi().event_handler('OnSipPhoneCallTimeoutNoResponse', __name__)

                if self.current_call.info().call_time > self.max_call_time:
                    logger.info("max call time reached - hangup current call after %s seconds", self.max_call_time)
                    self.current_call.hangup()
                    DoorPi().event_handler('OnSipPhoneCallTimeoutMaxCalltime', __name__)
            except:
                pass

    def call(self, number):
        DoorPi().event_handler('BeforeSipPhoneMakeCall', __name__, {'number':number})
        logger.debug("call(%s)",str(number))

        self.lib.thread_register('call_theard')

        sip_server = doorpi.sipphone.pjsua_lib.Config.sipphone_server()
        sip_uri = "sip:"+str(number)+"@"+str(sip_server)

        if self.lib.verify_sip_url(sip_uri) is not 0:
            logger.warning("SIP-URI %s is not valid (Errorcode: %s)", sip_uri, self.lib.verify_sip_url(sip_uri))
            return false
        else:
            logger.debug("SIP-URI %s is valid", sip_uri)

        DoorPi().event_handler('OnSipPhoneMakeCall', __name__)
        if not self.current_call or self.current_call.is_valid() is 0:
            lck = self.lib.auto_lock()
            self.current_callcallback = SipPhoneCallCallBack()
            self.current_call = self.__account.make_call(
                sip_uri,
                self.current_callcallback
            )
            del lck

        elif self.current_call.info().remote_uri == sip_uri:
            if self.current_call.info().total_time <= 1:
                logger.debug("same call again while call is running since %s seconds? -> skip", str(self.current_call.info().total_time))
            else:
                logger.debug("press twice with call duration > 1 second? Want to hangup current call? OK...")
                #self.current_call.hangup()
                self.lib.hangup_all()
        else:
            logger.debug("new call needed? hangup old first...")
            try:
                # self.current_call.hangup()
                self.lib.hangup_all()
            except pj.Error as e:
                logger.exception("Exception: %s", str(e))
            self.call(Number)

        DoorPi().event_handler('AfterSipPhoneMakeCall', __name__)
        return self.current_call

    def is_admin_number(self, remote_uri = None):
        logger.debug("is_admin_number (%s)",remote_uri)

        if remote_uri is None:
            if self.current_call is not None:
                remote_uri = self.current_call.info().remote_uri
            else:
                logger.debug("couldn't catch current call - no parameter and no current_call from doorpi itself")
                return False

        possible_admin_numbers = DoorPi().config.get_keys('AdminNumbers')
        for admin_number in possible_admin_numbers:
            if admin_number == "*":
                logger.info("admin numbers are deactivated by using '*' as single number")
                return True
            if "sip:"+admin_number+"@" in remote_uri:
                logger.debug("%s is an adminnumber", remote_uri)
                return True
            if "sip:"+admin_number is remote_uri:
                logger.debug("%s is adminnumber %s", remote_uri, admin_number)
                return True
        logger.debug("%s is not an adminnumber", remote_uri)
        return False

    def hangup(self):
        if self.current_call:
            logger.debug("Received hangup request, cancelling current call")
            self.lib.hangup_all()
        else:
            logger.debug("Ignoring hangup request as there is no ongoing call")

