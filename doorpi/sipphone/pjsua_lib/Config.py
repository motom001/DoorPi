#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import doorpi
import pjsua as pj

SIPPHONE_SECTION = 'SIP-Phone'
conf = doorpi.DoorPi().config

def call_timeout():
    return conf.get_int(SIPPHONE_SECTION, 'call_timeout', 30)

def max_call_time():
    return conf.get_int(SIPPHONE_SECTION, 'max_call_time', 120)

def sipphone_server():
    return conf.get(SIPPHONE_SECTION, 'server')

def pj_log(level, msg, length):
    # beautify output - remove date / time an line break
    length_date_and_time = len('15:22:35.695 ')
    length_linebreak = len('\n')
    msg = str(msg[length_date_and_time:-length_linebreak])
    # now it's a beautiful msg
    if level == 4: logger.trace("PJ: %s",msg)
    if level == 3: logger.debug("PJ: %s",msg)
    if level == 2: logger.info("PJ: %s",msg)
    if level == 1: logger.warning("PJ: %s",msg)
    if level == 0: logger.error("PJ: %s",msg)

def create_UAConfig():
    logger.debug("create_UAConfig")
    # Doc: http://www.pjsip.org/python/pjsua.htm#UAConfig
    UAConfig = pj.UAConfig()
    UAConfig.max_calls = conf.get_int(SIPPHONE_SECTION, 'ua.max_calls', 1)
    UAConfig.nameserver = conf.get_list(SIPPHONE_SECTION, 'ua.nameserver', [])
    UAConfig.stun_domain = conf.get(SIPPHONE_SECTION, 'ua.stun_domain', '')
    UAConfig.stun_host = conf.get(SIPPHONE_SECTION, 'ua.stun_host', '')
    UAConfig.user_agent = 'DoorPi'
    return UAConfig

def create_MediaConfig():
    logger.debug("create_MediaConfig")
    # Doc: http://www.pjsip.org/python/pjsua.htm#MediaConfig
    MediaConfig = pj.MediaConfig()
    MediaConfig.audio_frame_ptime = conf.get_int(SIPPHONE_SECTION, 'media.audio_frame_ptime', 20)
    MediaConfig.channel_count = conf.get_int(SIPPHONE_SECTION, 'media.channel_count', 1)
    MediaConfig.clock_rate = conf.get_int(SIPPHONE_SECTION, 'media.clock_rate', 8000)
    MediaConfig.ec_options = conf.get_int(SIPPHONE_SECTION, 'media.ec_options', 0)
    MediaConfig.ec_tail_len = conf.get_int(SIPPHONE_SECTION, 'media.ec_tail_len', 1024)
    MediaConfig.enable_ice = conf.get_bool(SIPPHONE_SECTION, 'media.enable_ice', True)
    MediaConfig.enable_turn = conf.get_bool(SIPPHONE_SECTION, 'media.enable_turn', False)
    MediaConfig.ilbc_mode = conf.get_int(SIPPHONE_SECTION, 'media.ilbc_mode', 30)
    MediaConfig.jb_max = conf.get_int(SIPPHONE_SECTION, 'media.jb_max', -1)
    MediaConfig.jb_min = conf.get_int(SIPPHONE_SECTION, 'media.jb_min', -1)
    MediaConfig.max_media_ports = conf.get_int(SIPPHONE_SECTION, 'media.max_media_ports', 32)
    MediaConfig.no_vad = conf.get_bool(SIPPHONE_SECTION, 'media.no_vad', False)
    MediaConfig.ptime = conf.get_int(SIPPHONE_SECTION, 'media.ptime', 0)
    MediaConfig.quality = conf.get_int(SIPPHONE_SECTION, 'media.quality', 10)
    MediaConfig.rx_drop_pct = conf.get_int(SIPPHONE_SECTION, 'media.rx_drop_pct', 0)
    MediaConfig.snd_auto_close_time = conf.get_int(SIPPHONE_SECTION, 'media.snd_auto_close_time', 5)
    MediaConfig.snd_clock_rate = conf.get_int(SIPPHONE_SECTION, 'media.snd_clock_rate', 0)
    MediaConfig.turn_conn_type = conf.get_int(SIPPHONE_SECTION, 'media.turn_conn_type', 17)
    #TODO: string to http://www.pjsip.org/python/pjsua.htm#AuthCred
    MediaConfig.turn_cred = None
    MediaConfig.turn_server = conf.get(SIPPHONE_SECTION, 'media.turn_server', '')
    MediaConfig.tx_drop_pct = conf.get_int(SIPPHONE_SECTION, 'media.tx_drop_pct', 0)
    return MediaConfig

def create_LogConfig():
    logger.debug("create_LogConfig")
    # Doc: http://www.pjsip.org/python/pjsua.htm#LogConfig
    LogConfig = pj.LogConfig(
        callback = pj_log,
        level = conf.get_int(SIPPHONE_SECTION, 'log.level', 1),
        console_level = conf.get_int(SIPPHONE_SECTION, 'log.console_level', 1)
    )
    return LogConfig

def create_AccountConfig():
    logger.debug("create_AccountConfig")
    # Doc: http://www.pjsip.org/python/pjsua.htm#AccountConfig
    server = conf.get(SIPPHONE_SECTION, "sipserver_server")
    username = conf.get(SIPPHONE_SECTION, "sipserver_username")
    password = conf.get(SIPPHONE_SECTION, "sipserver_password")
    realm = conf.get(SIPPHONE_SECTION, "sipserver_realm")

    AccountConfig = pj.AccountConfig()
    AccountConfig.id = "sip:" + username + "@" + server
    AccountConfig.reg_uri = "sip:" + server
    AccountConfig.auth_cred = [ pj.AuthCred(realm, username, password) ]
    AccountConfig.allow_contact_rewrite = conf.get_bool(SIPPHONE_SECTION, 'account.allow_contact_rewrite', 0)
    AccountConfig.reg_timeout = conf.get_int(SIPPHONE_SECTION, 'account.reg_timeout', 10)

    return AccountConfig

def create_TransportConfig():
    logger.debug("create_TransportConfig")
    # Doc: http://www.pjsip.org/python/pjsua.htm#TransportConfig
    TransportConfig = pj.TransportConfig(
        port = conf.get_int(SIPPHONE_SECTION, 'transport.port', 0),
        bound_addr = conf.get(SIPPHONE_SECTION, 'transport.bound_addr', ''),
        public_addr = conf.get(SIPPHONE_SECTION, 'transport.public_addr', '')
    )
    return TransportConfig
