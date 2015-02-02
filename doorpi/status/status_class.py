#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

import json
from datetime import datetime

class DoorPiStatus(object):

    __status = {}
    @property
    def dictionary(self): return self.__status

    @property
    def json(self): return json.dumps(self.__status)

    @property
    def json_beautified(self): return json.dumps(self.__status, sort_keys=True, indent=4)

    def __init__(self, DoorPiObject):
        self.collect_status(DoorPiObject)

    def collect_status(self, DoorPiObject):
        self.__status['status_time'] = str(datetime.now())
        self.__status['additional_informations'] = DoorPiObject.additional_informations
        self.__status['configfile'] = self.collect_status_from_config(DoorPiObject.config)
        self.__status['keyboard'] = self.collect_status_from_keyboard(DoorPiObject.keyboard)
        self.__status['sipphone'] = self.collect_status_from_sipphone(DoorPiObject.sipphone)
        self.__status['event_handler'] = self.collect_status_from_event_handler(DoorPiObject.event_handler)

    def collect_status_from_event_handler(self, event_handler):
        status = {}
        status['sources'] = event_handler.sources
        status['events'] = event_handler.events
        status['events_by_source'] = event_handler.events_by_source

        status['actions'] = {}
        for event in event_handler.actions:
            status['actions'][event] = []
            for action in event_handler.actions[event]:
                status['actions'][event].append(str(action))

        status['threads'] = str(event_handler.threads)
        status['idle'] = str(event_handler.idle)
        return status

    def collect_status_from_config(self, configobject):
        status = {}
        status['config'] = configobject.all
        return status

    def collect_status_from_sipphone(self, sipphone):
        if sipphone.name == 'PJSUA wrapper': return self.collect_status_from_sipphone_pjsua(sipphone)
        else: return {'sipphone': 'not detected'}

    def collect_status_from_sipphone_pjsua(self, sipphone):
        status = {}

        sipphone.lib.thread_register('status_thread')

        status['record_filename'] = sipphone.recorder.record_filename
        status['last_recorder_filename'] = sipphone.recorder.last_record_filename

        status['player_filename'] = sipphone.player.player_filename

        codecs = {}
        for codec in sipphone.lib.enum_codecs():
            codecs[codec.name] = {
                'avg_bps': codec.avg_bps,
                'channel_count': codec.channel_count,
                'clock_rate': codec.clock_rate,
                'frm_ptime': codec.frm_ptime,
                'plc_enabled': codec.plc_enabled,
                'priority': codec.priority,
                'pt': codec.pt,
                'ptime': codec.ptime,
                'vad_enabled': codec.vad_enabled
            }
        status['codecs'] = codecs

        sounddevices = {}
        for sounddevice in sipphone.lib.enum_snd_dev():
            sounddevices[sounddevice.name] = {
                'default_clock_rate': sounddevice.default_clock_rate,
                'input_channels': sounddevice.input_channels,
                'output_channels': sounddevice.output_channels
            }
        status['sounddevices'] = sounddevices

        if sipphone.current_call is not None:
            status['current_call'] = sipphone.current_call.dump_status().split('\n')
            status['level_incoming'] = sipphone.lib.conf_get_signal_level(0)[0] # tx_level
            status['level_outgoing'] = sipphone.lib.conf_get_signal_level(0)[1] # rx_level

            call_info = sipphone.current_call.info()
            status['CallInfo'] = {}
            status['CallInfo']['account'] = str(call_info.account)
            status['CallInfo']['call_time'] = call_info.call_time
            status['CallInfo']['conf_slot'] = call_info.conf_slot
            status['CallInfo']['contact'] = call_info.contact
            status['CallInfo']['last_code'] = call_info.last_code
            status['CallInfo']['last_reason'] = call_info.last_reason
            status['CallInfo']['media_dir'] = call_info.media_dir
            status['CallInfo']['media_state'] = call_info.media_state
            status['CallInfo']['remote_contact'] = call_info.remote_contact
            status['CallInfo']['remote_uri'] = call_info.remote_uri
            status['CallInfo']['role'] = call_info.role
            status['CallInfo']['sip_call_id'] = call_info.sip_call_id
            status['CallInfo']['state'] = call_info.state
            status['CallInfo']['state_text'] = call_info.state_text
            status['CallInfo']['total_time'] = call_info.total_time
            status['CallInfo']['uri'] = call_info.uri
        else:
            status['CallInfo'] = {}
            status['current_call'] = None
            status['level_incoming'] = None
            status['level_outgoing'] = None

        return status

    def collect_status_from_keyboard(self, keyboard):
        status = {}
        status['name'] = keyboard.name

        inputpins = {}
        for input_pin in keyboard.input_pins:
            inputpins[input_pin] = keyboard.status_inputpin(input_pin)
        status['inputpins'] = inputpins

        #TODO: Status vom Output abfragen und übersichtlich darstellen als dict
        #outputpins = {}
        #for output_pin in keyboard.output_pins:
        #    outputpins[output_pin] = keyboard.status_outputpin(output_pin)
        #status['outputpins'] = keyboard.status_outputpin(outputpins)

        return status