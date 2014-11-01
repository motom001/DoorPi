#!/usr/bin/python

import threading
import datetime
import time
import logging
import os
import pjsua as pj
from keypad import *

import logging

# TODO: -> metadata.py
SCRIPT_NAME = "DoorPi 1.0"

# TODO: -> configfile
LOG_LEVEL = 0
SIP_SERVER="192.168.178.1"
SIP_USER="621"
SIP_PASS="raspberry"
SIP_REALM="fritz.box"
SIP_LOCAL_PORT=5072

def log(msg, level = 1):
    sys.stdout.write("["+str(datetime.datetime.now())+"- "+str(level)+"] "+ msg+"\r\n")

def pj_log(level, msg, length):
    log(msg, 4-level)

def generate_dial_tone(filename = 'dialtone.wav', volume = 100):
    # generate wav file containing sine waves
    # FB36 - 20120617
    log("Start generate_dial_tone("+filename+", "+str(volume), 0)
    import math, wave, array
    duration = 3 # seconds
    freq = 440 # of cycles per second (Hz) (frequency of the sine waves)
    data = array.array('h') # signed short integer (-32768 to 32767) data
    sampleRate = 44100 # of samples per second (standard)
    numChan = 1 # of channels (1: mono, 2: stereo)
    dataSize = 2 # 2 bytes because of using signed short integers => bit depth = 16
    numSamplesPerCyc = int(sampleRate / freq)
    numSamples = sampleRate * duration
    for i in range(numSamples / 2):
        sample = 32767 * float(volume) / 100
        sample *= math.sin(math.pi * 2 * (i % numSamplesPerCyc) / numSamplesPerCyc)
        data.append(int(sample))
    for i in range(numSamples / 2):
        sample = 0
        data.append(int(sample))
    f = wave.open(filename, 'w')
    f.setparams((numChan, dataSize, sampleRate, numSamples, "NONE", "Uncompressed"))
    f.writeframes(data.tostring())
    f.close()

class DBCallCallback(pj.CallCallback):

    def __init__(self, call=None):
        pj.CallCallback.__init__(self, call)
        
    def on_media_state(self):
        print "***** ON MEDIA STATE " , self.call.info()
        if self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
            pj.Lib.instance().conf_connect(call_slot, 0)
            pj.Lib.instance().conf_connect(0, call_slot)
            print "Media is now active"
        else:
            print "Media is inactive"
            
    def on_state(self):
        print "**** ON STATE ", self.call
        print self.call.dump_status()
        #pj.CallCallback.on_state(self)
        
class DBAccountCallback(pj.AccountCallback):
    sem = None

    def __init__(self, account = None):
        pj.AccountCallback.__init__(self, account)

    def wait(self):
        self.sem = threading.Semaphore(0,verbose=True)
        self.sem.acquire()

    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()
    def on_incoming_call(self, call):
        cb = DBCallCallback(call)
        call.set_callback(cb)
        call.answer(200,'')


class SipPhoneCallCallBack(pj.CallCallback):

    LOG = None
    cb_openDoor = None
    PlayerID = None
    Lib = None

    inAction = False

    def __init__(self, cb_openDoor, PlayerID = None, LOG = log, call = None):
        self.LOG = LOG
        self.LOG("init SipPhoneCallCallBack", 0)
        self.cb_openDoor = cb_openDoor
        self.PlayerID = PlayerID
        self.Lib = pj.Lib.instance()
        pj.CallCallback.__init__(self, call)

    def __del__(self):
        self.LOG("destroy SipPhoneCallCallBack", 0)
        self.destroy()

    def destroy(self):
        self.LOG("destroy SipPhoneCallCallBack", 0)

    def on_media_state(self):
        self.LOG("SipPhoneCallCallBack.on_media_state ("+str(self.call.info().media_state)+")",0)

    def on_state(self):
        self.LOG("SipPhoneCallCallBack.on_state ("+self.call.info().state_text+")",0)

        while self.inAction is not False:
            self.LOG("wait for finished action '"+self.inAction+"'", 0)
            time.sleep(0.1)

        if self.call.info().state in [pj.CallState.CONNECTING, pj.CallState.CONFIRMED] \
        and self.call.info().media_state == pj.MediaState.ACTIVE:
            # Connect the call to sound device
            call_slot = self.call.info().conf_slot
            if self.PlayerID is not None:
                self.Lib.conf_disconnect(self.Lib.player_get_slot(self.PlayerID), 0)
            self.Lib.conf_connect(call_slot, 0)
            self.Lib.conf_connect(0, call_slot)
            self.LOG("conneted Media to call_slot "+str(call_slot), 0)

        if self.call.info().state == pj.CallState.DISCONNECTED:
            call_slot = self.call.info().conf_slot
            self.Lib.conf_disconnect(call_slot, 0)
            self.Lib.conf_disconnect(0, call_slot)
            self.LOG("disconneted Media from call_slot "+str(call_slot), 0)

    def on_dtmf_digit(self, digits):
        self.LOG("SipPhoneCallCallBack.on_dtmf_digit: "+str(digits), 0)
        if digits == '#':
            # TODO: -> configfile
            self.inAction = "Open Door 0"
            self.LOG("SipPhoneCallCallBack.on_dtmf_digit: get request (#) for open Door - execute callback function", 0)
            self.cb_openDoor('0')
            self.inAction = False

class SipPhoneAccountCallBack(pj.AccountCallback):

    LOG = None

    def __init__(self, LOG = log, account = None):
        self.LOG = LOG
        self.LOG("init SipPhoneAccountCallBack", 0)
        pj.AccountCallback.__init__(self, account)

    def __del__(self):
        self.LOG("destroy SipPhoneAccountCallBack", 0)
        pj.AccountCallback.__del__(self)

    def on_incoming_call(self, call):
        self.LOG("SipPhoneAccountCallBack.on_incoming_call", 0)
        self.LOG("Incoming call from "+ str(call.info().remote_uri), 0)
        # TODO: -> configfile
        if call.info().remote_uri.startswith("506411"):
            self.LOG("Incoming Call from trusted number "+call.info().remote_uri+" -> autoanswer", 0)
            call.answer(200)
        else:
            call.answer(486, "Busy")
            return




class SipPhonePjsua:
    Lib = None
    Acc = None
    LOG = None

    PlayerID = None

    current_call = None
    current_callcallback = None


    def __init__(self, LOG = log):
        self.LOG = LOG
        self.LOG("init SipPhone with pjsua", 0)

        self.Lib = pj.Lib()
        try:
            self.Lib.init(
                    ua_cfg    = self.CreateUAConfig(),
                    media_cfg = self.CreateMediaConfig(),
                    log_cfg   = self.CreateLogConfig()
            )
            transport = self.Lib.create_transport(
                pj.TransportType.UDP,
                pj.TransportConfig(0)
            )

            self.Lib.start()

            self.Acc = self.Lib.create_account(
                acc_config = self.CreateAccountConfig(),
                set_default = True,
                cb = SipPhoneAccountCallBack()
            )

            self.LOG("Listening on: "+str(transport.info().host), 0)
            self.LOG("Port: "+str(transport.info().port), 0)

            # TODO: -> configfile
            wavfile = '/home/pi/DoorPi_1.0/station/ShortDialTone.wav'
            if os.path.isfile(wavfile) and os.access(wavfile, os.R_OK):
                self.LOG("wavefile exist and is readable", 0)
            else:
                self.LOG("wavefile is missing or not readable", 0)
                generate_dial_tone(wavfile, 100)

            self.PlayerID = self.Lib.create_player(
                filename = wavfile,
                loop = True
            )


        except pj.Error, e:
            self.LOG("Exception: " + str(e), 3)
            self.Lib.destroy()
            self.Lib = None

    def __del__(self):
        self.destroy()

    def destroy(self):
        self.LOG("destroy SipPhone", 0)
        if self.current_callcallback is not None:
            self.current_callcallback.destroy()
            self.current_callcallback = None
            del self.current_callcallback

        if self.Acc is not None:
            self.Acc.delete()
            self.Acc = None
            del self.Acc

        if self.PlayerID:
            self.Lib.player_destroy(self.PlayerID)
            self.PlayerID = None
            del self.PlayerID

        if self.Lib is not None:
            self.Lib.destroy()
            self.Lib = None
            del self.Lib

    def selftest(self):
        self.LOG("SipPhone.selftest", 0)

    def PjLog(self, level, msg, length):
        self.LOG(msg, 4-level)

    def CreateUAConfig(self):
        # Doc: http://www.pjsip.org/python/pjsua.htm#UAConfig
        # TODO: -> configfile
        UAConfig = pj.UAConfig()
        UAConfig.user_agent = SCRIPT_NAME
        #ua.max_calls = 1
        return UAConfig

    def CreateMediaConfig(self):
        # Doc: http://www.pjsip.org/python/pjsua.htm#MediaConfig
        # TODO: -> configfile
        MediaConfig = pj.MediaConfig()
        #MediaConfig.no_vad = False
        #MediaConfig.ec_tail_len = 800
        MediaConfig.clock_rate = 8000
        return MediaConfig

    def CreateLogConfig(self):
        # Doc: http://www.pjsip.org/python/pjsua.htm#LogConfig
        # TODO: -> configfile
        LogConfig = pj.LogConfig(level=LOG_LEVEL, callback=self.PjLog)
        return LogConfig

    def CreateAccountConfig(self):
        # Doc: http://www.pjsip.org/python/pjsua.htm#AccountConfig
        # TODO: -> configfile
        AccountConfig = pj.AccountConfig()
        AccountConfig.id = "sip:" + SIP_USER + "@" + SIP_SERVER
        AccountConfig.reg_uri = "sip:" + SIP_SERVER
        AccountConfig.auth_cred = [ pj.AuthCred(SIP_REALM, SIP_USER, SIP_PASS) ]
        AccountConfig.allow_contact_rewrite = False
        AccountConfig.reg_timeout = 1
        return AccountConfig

    def makeCall(self, Number, cb_openDoor):
        self.LOG("SipPhone.makeCall("+str(Number)+")", 0)
        if not self.current_call or self.current_call.is_valid() is 0:
            lck = self.Lib.auto_lock()
            self.current_callcallback = SipPhoneCallCallBack(
                cb_openDoor = cb_openDoor,
                PlayerID = self.PlayerID
            )
            self.current_call = self.Acc.make_call(
                "sip:"+Number+"@"+SIP_SERVER,
                self.current_callcallback
            )
            del lck

            if self.PlayerID is not None:
                self.Lib.conf_connect(self.Lib.player_get_slot(self.PlayerID), 0)

        elif self.current_call.info().remote_uri == "sip:"+Number+"@"+SIP_SERVER:
            if self.current_call.info().total_time <= 1:
                self.LOG("same call again while call is running since "+str(self.current_call.info().total_time)+" seconds? - skip",0)
            else:
                self.LOG("press twice with call duration > 1 second? Want to hangup current call? OK...",0)
                if self.PlayerID is not None:
                    self.Lib.conf_disconnect(self.Lib.player_get_slot(self.PlayerID), 0)
                self.current_call.hangup()
        else:
            self.LOG("new call needed? hangup old first...",0)
            try:
                self.current_call.hangup()
            except pj.Error, e:
                self.LOG("Exception: " + str(e),0)

            if self.PlayerID is not None:
                self.Lib.conf_disconnect(self.Lib.player_get_slot(self.PlayerID), 0)
            del self.current_call
            self.makeCall(Number, cb_openDoor)

class DoorPi:

    LOG = None
    keyboard = None
    SipPhone = None

    def __init__(self, LOG = log, keyboard = PiFace, SipPhone = SipPhonePjsua):
        self.LOG = LOG
        self.LOG("init DoorPi", 0)
        self.keyboard = self.init_keyboard(keyboard, True)
        self.SipPhone = self.init_SipPhone(SipPhone, True)

    def __del__(self):
        self.destroy()

    def destroy(self):
        self.LOG("destroy DoorPi", 0)
        if self.SipPhone is not None:
            self.SipPhone.destroy()
            self.SipPhone = None
            del self.SipPhone

        if self.keyboard is not None:
            self.keyboard.destroy()
            self.keyboard = None
            del self.keyboard

    def init_keyboard(self, Keyboard, withSelfTest = False):
        self.LOG("DoorPi.init_keyboard", 0)
        ReturnKeyboard = Keyboard(self.LOG)
        # TODO: -> configfile
        ReturnKeyboard.InputPins = [0,1,2,3,4,5,6,7]
        ReturnKeyboard.OutputPins = [0,1,2,3,4,5,6,7]
        if (withSelfTest): ReturnKeyboard.selftest()
        return ReturnKeyboard

    def init_SipPhone(self, SipClass = SipPhonePjsua, withSelfTest = False):
        self.LOG("DoorPi.init_SipPhone", 0)
        SipPhone = SipClass(self.LOG)
        if (withSelfTest): SipPhone.selftest()
        return SipPhone

    def run(self):
        self.LOG("DoorPi.run", 0)
        while True:
            Key = self.keyboard.IfKeyPressed()
            if Key == 3:
                self.LOG("DoorPi.run: Key "+str(Key)+" is pressed - break", 0)
                break

            if Key >= 0:
                self.LOG("DoorPi.run: Key "+str(Key)+" is pressed - start makeCall", 0)
                # TODO: -> configfile
                if Key == 0: self.makeCall('5973922')
                if Key == 1: self.makeCall('01783558321')
                time.sleep(1) # for fat fingers

            if int(round(time.time())) % 2:
                self.keyboard.DefineOutput(3, 1)
            else:
                self.keyboard.DefineOutput(3, 0)
            time.sleep(0.1)

    def CheckCall(self):
        if self.SipPhone.current_call is None:
            return True
        if self.SipPhone.current_call.is_valid() == 0:
            return True
        if self.SipPhone.current_call.info().state == 6:
            return True

        self.LOG("current_call.info().state "+str(self.SipPhone.current_call.info().state),0)
        return False

    def makeCall(self, PhoneNumber):
        self.LOG("call DoorPi.make_call("+PhoneNumber+")", 0)
        self.SipPhone.makeCall(PhoneNumber, self.openDoor)

    def openDoor(self, stationnumber = '0'):
        self.LOG("call DoorPi.openDoor", 0)
        # TODO: -> configfile
        if stationnumber == '0':
            self.keyboard.SetOutput(0, 3)
        elif (stationnumber == '1'):
            self.keyboard.SetOutput(1, 3)
