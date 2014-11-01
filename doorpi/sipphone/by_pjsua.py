#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

#import threading
#import datetime
#import time
import pjsua
import pjsua_lib.SipPhoneAccountCallBack
import pjsua_lib.SipPhoneCallCallBack
from media.CreateDialTone import generate_dial_tone
from doorpi import DoorPi

import os # used by: Pjsua.start

class Pjsua:
    __Lib = None
    __Acc = None

    __PlayerID = None

    __current_call = None
    __current_callcallback = None

    def __init__(self):
        logger.debug("__init__")

    def start(self):
        self.__Lib = pjsua.Lib()
        try:
            logger.debug("init Lib")
            self.__Lib.init(
                ua_cfg      = self.create_UAConfig(),
                media_cfg   = self.create_MediaConfig(),
                log_cfg     = self.create_LogConfig()
            )

            logger.debug("init transport")
            transport = self.__Lib.create_transport(
                type        = pjsua.TransportType.UDP,
                cfg         = self.create_TransportConfig()
            )

            logger.debug("Lib.start()")
            self.__Lib.start()

            logger.debug("init Acc")
            self.__Acc = self.__Lib.create_account(
                acc_config  = self.create_AccountConfig(),
                set_default = True,
                cb          = pjsua_lib.SipPhoneAccountCallBack.SipPhoneAccountCallBack()
            )

            logger.debug("Listening on: %s",str(transport.info().host))
            logger.debug("Port: %s",str(transport.info().port))

            wavefile = DoorPi().get_config().get("SIP-Phone", "dialtone")
            if os.path.isfile(wavefile) and os.access(wavefile, os.R_OK):
                logger.debug("wavefile '%s' exist and is readable", wavefile)
            elif wavefile is not '':
                logger.debug("wavefile is missing or not readable - create it now")
                generate_dial_tone(wavefile, 100)
                logger.debug("wavefile '%s' created", wavefile)
            else:
                logger.info("no wavefile for dialtone in configfile")

            if wavefile:
                self.__PlayerID = self.__Lib.create_player(
                    filename = wavefile,
                    loop = True
                )
                logger.debug("create Player with wavefile for dialtone")

            logger.debug("start successfully")

        except pjsua.Error, e:
            logger.critical("Exception: %s", str(e))
            self.__Lib.destroy()
            self.__Lib = None
            raise Exception("error while init sipphone with pjsua.Error: %s", str(e))
        #except:
        #    self.__Lib.destroy()
        #    self.__Lib = None
        #    raise Exception("error while init sipphone with non defined exception")

    def __del__(self):
        self.destroy()

    def destroy(self):
        logger.debug("destroy")
        if self.__current_callcallback is not None:
            self.__current_callcallback.destroy()
            self.__current_callcallback = None
            del self.__current_callcallback

        if self.__Acc is not None:
            self.__Acc.delete()
            self.__Acc = None
            del self.__Acc

        if self.__PlayerID:
            self.__Lib.player_destroy(self.PlayerID)
            self.__PlayerID = None
            del self.__PlayerID

        if self.__Lib is not None:
            self.__Lib.destroy()
            self.__Lib = None
            del self.__Lib

    def selftest(self):
        logger.debug("selftest")

    def pj_log(self, level, msg, length):
        # beautify output - remove date / time an line break
        length_date_and_time = len('15:22:35.695 ')
        length_linebreak = len('\n')
        msg = str(msg[length_date_and_time:-length_linebreak])
        # now it's a beautiful msg

        if level == 4: logger.debug("PJ: %s",msg)
        if level == 3: logger.info("PJ: %s",msg)
        if level == 2: logger.warning("PJ: %s",msg)
        if level == 1: logger.error("PJ: %s",msg)
        if level == 0: logger.critical("PJ: %s",msg)

    def create_UAConfig(self):
        logger.debug("CreateUAConfig")
        # Doc: http://www.pjsip.org/python/pjsua.htm#UAConfig
        # TODO: -> configfile
        UAConfig = pjsua.UAConfig()
        UAConfig.user_agent = __name__
        #ua.max_calls = 1
        return UAConfig

    def create_MediaConfig(self):
        logger.debug("CreateMediaConfig")
        # Doc: http://www.pjsip.org/python/pjsua.htm#MediaConfig
        # TODO: -> configfile
        MediaConfig = pjsua.MediaConfig()
        #MediaConfig.no_vad = False
        #MediaConfig.ec_tail_len = 800
        MediaConfig.clock_rate = 8000
        return MediaConfig

    def create_LogConfig(self):
        logger.debug("CreateLogConfig")
        # Doc: http://www.pjsip.org/python/pjsua.htm#LogConfig
        # TODO: -> configfile
        LogConfig = pjsua.LogConfig(
            callback = self.pj_log,
            level = 0,
            console_level = 5
        )
        return LogConfig

    def create_AccountConfig(self):
        logger.debug("CreateAccountConfig")
        # Doc: http://www.pjsip.org/python/pjsua.htm#AccountConfig
        server = DoorPi().get_config().get("SIP-Phone", "server")
        username = DoorPi().get_config().get("SIP-Phone", "username")
        password = DoorPi().get_config().get("SIP-Phone", "password")
        realm = DoorPi().get_config().get("SIP-Phone", "realm")

        logger.info("try to create AccountConfig")
        logger.debug("username:     %s", username)
        logger.debug("password:     %s", '******')
        logger.debug("server:       %s", server)
        logger.debug("realm:        %s", realm)

        AccountConfig = pjsua.AccountConfig()
        AccountConfig.id = "sip:" + username + "@" + server
        AccountConfig.reg_uri = "sip:" + server
        AccountConfig.auth_cred = [ pjsua.AuthCred(realm, username, password) ]
        AccountConfig.allow_contact_rewrite = False
        AccountConfig.reg_timeout = 1
        return AccountConfig

    def create_TransportConfig(self):
        logger.debug("CreateTransportConfig")
        # Doc: http://www.pjsip.org/python/pjsua.htm#TransportConfig
        TransportConfig = pjsua.TransportConfig(0)
        return TransportConfig

    def make_call(self, Number):
        logger.debug("makeCall(%s)",str(Number))

        sip_server = DoorPi().get_config().get("SIP-Phone", "server")

        if not self.__current_call or self.__current_call.is_valid() is 0:
            lck = self.__Lib.auto_lock()
            self.__current_callcallback = pjsua_lib.SipPhoneCallCallBack.SipPhoneCallCallBack()
            self.__current_call = self.__Acc.make_call(
                "sip:"+Number+"@"+sip_server,
                self.__current_callcallback
            )
            del lck

            if self.__PlayerID is not None:
                self.__Lib.conf_connect(self.__Lib.player_get_slot(self.__PlayerID), 0)

        elif self.__current_call.info().remote_uri == "sip:"+Number+"@"+sip_server:
            if self.__current_call.info().total_time <= 1:
                logger.debug("same call again while call is running since %s seconds? -> skip", str(self.__current_call.info().total_time))
            else:
                logger.debug("press twice with call duration > 1 second? Want to hangup current call? OK...")
                if self.__PlayerID is not None:
                    self.__Lib.conf_disconnect(self.__Lib.player_get_slot(self.__PlayerID), 0)
                self.__current_call.hangup()
        else:
            logger.debug("new call needed? hangup old first...")
            try:
                self.__current_call.hangup()
            except pj.Error, e:
                logger.critical("Exception: %s", str(e))

            if self.__PlayerID is not None:
                self.Lib.conf_disconnect(self.Lib.player_get_slot(self.__PlayerID), 0)
            del self.__current_call
            self.make_call(Number)

        return self.__current_call