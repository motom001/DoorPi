#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import datetime # used by: get_new_recorder, start
import os # used by: Pjsua.start

import pjsua

import pjsua_lib.SipPhoneAccountCallBack
import pjsua_lib.SipPhoneCallCallBack

from media.CreateDialTone import generate_dial_tone
from doorpi import DoorPi

class Pjsua:
    __Lib = None
    __Acc = None

    __PlayerID = None
    def get_player_id(self):
        return self.__PlayerID

    __record_while_dialing = None
    def get_record_while_dialing(self):
        return self.__record_while_dialing

    __RecorderFilename = None
    def get_parsed_recorder_filename(self):
        if self.__RecorderFilename is None: return None

        parsed_recorder_filename = self.__RecorderFilename.replace(
            "%LastKey%",
            str(DoorPi().get_keyboard().get_last_key())
        )
        parsed_recorder_filename = datetime.datetime.now().strftime(parsed_recorder_filename)
        return parsed_recorder_filename

    __RecorderID = None
    def get_recorder_id(self):
        return self.__RecorderID
    def get_recorder_slot(self):
        rec_id = self.get_recorder_id()
        if rec_id is None:
            return None
        else:
            return self.__Lib.recorder_get_slot(rec_id)
    def get_new_recorder_as_id(self):
        parsed_recorder_filename = self.get_parsed_recorder_filename()
        if parsed_recorder_filename is None: return None

        self.__RecorderID = self.__Lib.create_recorder(
            filename = parsed_recorder_filename
        )
        logger.debug('created new recorder with filename %s', parsed_recorder_filename)
        return self.get_recorder_id()
    def get_new_recorder_as_slot(self):
        self.get_new_recorder_as_id()
        return self.get_recorder_slot()
    def stop_recorder(self):
        self.__Lib.recorder_destroy(self.get_recorder_id())
        self.__RecorderID = None
    def stop_recorder_if_exists(self):
        rec_id = self.get_recorder_id()
        if rec_id is None or rec_id is '':
            return
        self.stop_recorder()

    __current_call = None
    def get_current_call(self):
        return self.__current_call
    def set_current_call(self, call):
        if call is None:
            self.__current_call = None
            return None

        if call.info().remote_uri == self.get_current_call().info().remote_uri and \
                        call.info().contact == self.get_current_call().info().contact:
            return self.__current_call

        if self.get_current_call() is not None:
            logger.warning("replace current_call while current_call is not None")

        self.__current_call = call
        return self.get_current_call()

    __current_callcallback = None
    def get_current_callback(self):
        return self.__current_callcallback
    def set_current_callback(self, callback):
        if self.__current_callcallback is callback: return self.get_current_callback()
        if callback is None: self.__current_callcallback = None

        if self.__current_callcallback is not None:
            logger.warning("replace current_callcallback while current_callcallback is not None")
        self.__current_callcallback = callback
        return self.get_current_callback()

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

            dialtone = DoorPi().get_config().get("DoorPi", "dialtone")
            if os.path.isfile(dialtone) and os.access(dialtone, os.R_OK):
                logger.debug("dialtone '%s' exist and is readable", dialtone)
            elif dialtone is not '':
                logger.debug("dialtone is missing or not readable - create it now")
                generate_dial_tone(dialtone, 100)
                logger.debug("dialtone '%s' created", dialtone)
            else:
                logger.info("no dialtone in configfile (Section [DoorPi], Parameter dialtone)")

            if dialtone:
                self.__PlayerID = self.__Lib.create_player(
                    filename = dialtone,
                    loop = True
                )
                logger.debug("create Player with dialtone")

            self.__RecorderFilename = DoorPi().get_config().get("DoorPi", "records")
            if self.__RecorderFilename is None or self.__RecorderFilename is '':
                logger.debug('no records in configfile (Section [DoorPi], Parameter records')
            else:
                logger.debug('use %s as recordfile', self.__RecorderFilename)
                logger.debug(' for example at this moment: %s', datetime.datetime.now().strftime(self.__RecorderFilename))

            self.__record_while_dialing = DoorPi().get_config().get("DoorPi", "record_while_dialing")
            if self.__record_while_dialing == 'true':
                logger.debug('record_while_dialing is true')
                self.__record_while_dialing = True
            else:
                logger.debug('record_while_dialing is not true (it is %s)', self.__record_while_dialing)
                self.__record_while_dialing = False

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

        if self.__current_call is not None:
            self.__current_call.hangup()
            self.__current_call = None
            del self.__current_call

        if self.__Acc is not None:
            self.__Acc.delete()
            self.__Acc = None
            del self.__Acc

        if self.__PlayerID:
            self.__Lib.player_destroy(self.__PlayerID)
            self.__PlayerID = None
            del self.__PlayerID

        if self.__RecorderID:
            self.__Lib.recorder_destroy(self.__RecorderID)
            self.__RecorderID = None
            del self.__RecorderID

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
            if self.get_parsed_recorder_filename() is not None and self.get_record_while_dialing() is True:
                self.__Lib.conf_connect(0, self.get_new_recorder_as_slot())

        elif self.__current_call.info().remote_uri == "sip:"+Number+"@"+sip_server:
            if self.__current_call.info().total_time <= 1:
                logger.debug("same call again while call is running since %s seconds? -> skip", str(self.__current_call.info().total_time))
            else:
                logger.debug("press twice with call duration > 1 second? Want to hangup current call? OK...")
                if self.__PlayerID is not None:
                    self.__Lib.conf_disconnect(self.__Lib.player_get_slot(self.__PlayerID), 0)

                self.stop_recorder_if_exists()
                self.__current_call.hangup()
        else:
            logger.debug("new call needed? hangup old first...")
            try:
                self.__current_call.hangup()
            except pj.Error, e:
                logger.critical("Exception: %s", str(e))

            if self.__PlayerID is not None:
                self.Lib.conf_disconnect(self.Lib.player_get_slot(self.__PlayerID), 0)

            self.stop_recorder_if_exists()
            del self.__current_call
            self.make_call(Number)

        return self.__current_call

    def is_admin_number(self, remote_uri = None):
        logger.debug("is_admin_number (%s)",remote_uri)

        if remote_uri is None:
            if self.__current_call is not None:
                remote_uri = self.__current_call().info().remote_uri
            else:
                logger.debug("couldn't catch current call - no parameter and no current_call from doorpi itself")
                return False

        possible_AdminNumbers = DoorPi().get_config().get_keys('AdminNumbers')
        for AdminNumber in possible_AdminNumbers:
            if "sip:"+AdminNumber+"@" in remote_uri:
                logger.debug("%s is an adminnumber", remote_uri)
                return True

        logger.debug("%s is not an adminnumber", remote_uri)
        return False