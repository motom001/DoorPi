#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

def get(*args, **kwargs):
    try:
        if len(kwargs['name']) == 0: kwargs['name'] = ['']
        if len(kwargs['value']) == 0: kwargs['value'] = ['']

        sipphone = kwargs['DoorPiObject'].sipphone

        status = {}
        for name_requested in kwargs['name']:
            status = {}
            sipphone.thread_register('status_thread')

            if name_requested in 'name':
                status['name'] = sipphone.name

            if name_requested in 'sound_codecs':
                status['sound_codecs'] = sipphone.sound_codecs
            if name_requested in 'sound_devices':
                status['sound_devices'] = sipphone.sound_devices

            if name_requested in 'sound_enable':
                if len(sipphone.sound_codecs) and len(sipphone.sound_devices):
                    status['sound_enable'] = True
                else:
                    status['sound_enable'] = False

            if name_requested in 'video_codecs':
                status['video_codecs'] = sipphone.video_codecs
            if name_requested in 'video_devices':
                status['video_devices'] = sipphone.video_devices

            if name_requested in 'video_enable':
                if len(sipphone.video_codecs) and len(sipphone.video_devices):
                    status['video_enable'] = True
                else:
                    status['video_enable'] = False

            if name_requested in 'recorder':
                status['has_recorder'] = True if sipphone.recorder else False
                if status['has_recorder']:
                    status['recorder_filename'] = sipphone.recorder.record_filename
                    status['recorder_parsed_filename'] = sipphone.recorder.parsed_record_filename

            if name_requested in 'player':
                status['has_player'] = True if sipphone.player else False
                if status['has_player']:
                    status['player_filename'] = sipphone.player.player_filename

            if name_requested in 'current_call':
                status['current_call'] = sipphone.current_call_dump

        return status
    except Exception as exp:
        logger.exception(exp)
        return {'Error': 'could not create '+str(__name__)+' object - '+str(exp)}

def is_active(doorpi_object):
    return True if doorpi_object.sipphone else False
