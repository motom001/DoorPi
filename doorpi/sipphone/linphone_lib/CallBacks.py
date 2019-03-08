#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
logger.debug("%s loaded", __name__)

from time import sleep
import linphone
from doorpi import DoorPi

class LinphoneCallbacks:

    @property
    def used_callbacks(self): return {
        #http://www.linphone.org/docs/liblinphone/struct__LinphoneCoreVTable.html
        #'global_state_changed': self.global_state_changed, #Notifies global state changes
        #'registration_state_changed': self.registration_state_changed, #Notifies registration state changes
        'call_state_changed': self.call_state_changed, #Notifies call state changes
        #'notify_presence_received': self.notify_presence_received, #Notify received presence events
        #'new_subscription_requested': self.new_subscription_requested, #Notify about pending presence subscription request
        #'auth_info_requested': self.auth_info_requested, #Ask the application some authentication information
        #'call_log_updated': self.call_log_updated, #Notifies that call log list has been updated
        #'message_received': self.message_received, #a message is received, can be text or external body
        #'is_composing_received': self.is_composing_received, #An is-composing notification has been received
        'dtmf_received': self.dtmf_received, #A dtmf has been received received
        #'refer_received': self.refer_received, #An out of call refer was received
        #'call_encryption_changed': self.call_encryption_changed, #Notifies on change in the encryption of call streams
        #'transfer_state_changed': self.transfer_state_changed, #Notifies when a transfer is in progress
        #'buddy_info_updated': self.buddy_info_updated, #a LinphoneFriend's BuddyInfo has changed
        #'call_stats_updated': self.call_stats_updated, #Notifies on refreshing of call's statistics.
        #'info_received': self.info_received, #Notifies an incoming informational message received.
        #'subscription_state_changed': self.subscription_state_changed, #Notifies subscription state change
        #'notify_received': self.notify_received, #Notifies a an event notification, see linphone_core_subscribe()
        #'configuring_status': self.configuring_status, #Notifies publish state change (only from LinphoneEvent api)
        #'network_reachable': self.network_reachable, #Callback to report IP network status (I.E up/down )
        #'log_collection_upload_state_changed': self.log_collection_upload_state_changed, #Callback to upload collected logs
        #'log_collection_upload_progress_indication': self.log_collection_upload_progress_indication #Callback to indicate log collection upload progress
    }

    @property
    def whitelist(self): return DoorPi().config.get_keys('AdminNumbers')

    def is_admin_number(self, remote_uri):
        logger.debug("is_admin_number (%s)",remote_uri)
        for admin_number in self.whitelist:
            if admin_number == "*":
                logger.info("admin numbers are deactivated by using '*' as single number")
                return True
            if "sip:"+admin_number+"@" in remote_uri:
                logger.debug("%s is adminnumber %s", remote_uri, admin_number)
                return True
            if "sip:"+admin_number is remote_uri:
                logger.debug("%s is adminnumber %s", remote_uri, admin_number)
                return True
        logger.debug("%s is not an adminnumber", remote_uri)
        return False

    __DTMF = ''
    __possible_DTMF = []

    def __init__(self):
        logger.debug("__init__")

        self._last_number_of_calls = 0

        DoorPi().event_handler.register_action('OnSipPhoneDestroy', self.destroy)

        DoorPi().event_handler.register_event('OnCallMediaStateChange', __name__)
        DoorPi().event_handler.register_event('OnMediaRequired', __name__)
        DoorPi().event_handler.register_event('OnMediaNotRequired', __name__)

        DoorPi().event_handler.register_event('OnCallStateChange', __name__)
        DoorPi().event_handler.register_event('OnCallStateConnect', __name__)
        DoorPi().event_handler.register_event('AfterCallStateConnect', __name__)
        DoorPi().event_handler.register_event('OnCallStateDisconnect', __name__)
        DoorPi().event_handler.register_event('AfterCallStateDisconnect', __name__)
        DoorPi().event_handler.register_event('OnCallStateDismissed', __name__)
        DoorPi().event_handler.register_event('OnCallStateReject', __name__)
        DoorPi().event_handler.register_event('OnCallStart', __name__)
        DoorPi().event_handler.register_event('OnDTMF', __name__)

        self.__possible_DTMF = DoorPi().config.get_keys('DTMF')
        for DTMF in self.__possible_DTMF:
            DoorPi().event_handler.register_event('OnDTMF_'+DTMF, __name__)

        DoorPi().event_handler.register_event('OnCallStart', __name__)
        DoorPi().event_handler.register_event('BeforeCallIncoming', __name__)
        DoorPi().event_handler.register_event('OnCallReconnect', __name__)
        DoorPi().event_handler.register_event('AfterCallReconnect', __name__)
        DoorPi().event_handler.register_event('OnCallBusy', __name__)
        DoorPi().event_handler.register_event('AfterCallBusy', __name__)
        DoorPi().event_handler.register_event('OnCallIncoming', __name__)
        DoorPi().event_handler.register_event('AfterCallIncoming', __name__)
        DoorPi().event_handler.register_event('OnCallReject', __name__)
        DoorPi().event_handler.register_event('AfterCallReject', __name__)
        #DoorPi().event_handler.register_event('AfterAccountRegState', __name__)

        DoorPi().event_handler('OnCallStart', __name__)

    def destroy(self):
        logger.debug("destroy")
        DoorPi().event_handler.unregister_source(__name__, True)

    def global_state_changed(self, core, global_state, message): pass
    def registration_state_changed(self, core, linphone_proxy_config, state, message): pass
    def call_state_changed(self, core, call, call_state, message):
        self.call_state_changed_handle(core, call, call_state, message)

        if core.calls_nb > 0 and self._last_number_of_calls == 0:
            DoorPi().event_handler('OnMediaRequired', __name__)
        elif self._last_number_of_calls is not core.calls_nb:
            DoorPi().event_handler('OnMediaNotRequired', __name__)
        self._last_number_of_calls = core.calls_nb

    def call_state_changed_handle(self, core, call, call_state, message):
        logger.debug("call_state_changed (%s - %s)", call_state, message)

        remote_uri = call.remote_address.as_string_uri_only()

        DoorPi().event_handler('OnCallStateChange', __name__, {
            'remote_uri': remote_uri,
            'call_state': call_state,
            'state': message
        })

        if call_state == linphone.CallState.Idle:
            pass
        elif call_state == linphone.CallState.IncomingReceived:
            DoorPi().event_handler('BeforeCallIncoming', __name__, {'remote_uri': remote_uri})
            if core.current_call and core.current_call.state > linphone.CallState.IncomingReceived:
                logger.debug("Incoming call while another call is active")
                logger.debug("- incoming.remote_uri: %s", call)
                logger.debug("- current.remote_uri : %s", core.current_call)

                if core.current_call.remote_address.as_string_uri_only() == remote_uri:
                    logger.info("Current call is incoming call - quitting current and connecting to incoming. Maybe connection reset?")
                    DoorPi().event_handler('OnCallReconnect', __name__, {'remote_uri': remote_uri})
                    core.terminate_call(core.current_call)
                    DoorPi().sipphone.reset_call_start_datetime()
                    core.accept_call_with_params(call, DoorPi().sipphone.base_config)
                    DoorPi().event_handler('AfterCallReconnect', __name__)
                    return
                else:
                    if self.is_admin_number(remote_uri):
                        logger.info("Incoming and current call are different - incoming is AdminNumber, so hanging up current call")
                        DoorPi().event_handler('OnCallIncoming', __name__, {'remote_uri': remote_uri})
                        core.terminate_call(core.current_call)
                        DoorPi().sipphone.reset_call_start_datetime()
                        core.accept_call_with_params(call, DoorPi().sipphone.base_config)
                        DoorPi().event_handler('AfterCallIncoming', __name__, {'remote_uri': remote_uri})
                        return
                    else:
                        logger.info("Incoming and current call are different - sending busy signal to incoming call")
                        DoorPi().event_handler('OnCallBusy', __name__, {'remote_uri': remote_uri})
                        core.decline_call(call, linphone.Reason.Busy)
                        DoorPi().event_handler('AfterCallBusy', __name__)
                        return
            if self.is_admin_number(remote_uri):
                DoorPi().event_handler('OnCallIncoming', __name__, {'remote_uri': remote_uri})
                DoorPi().sipphone.reset_call_start_datetime()
                core.accept_call_with_params(call, DoorPi().sipphone.base_config)
                DoorPi().event_handler('AfterCallIncoming', __name__, {'remote_uri': remote_uri})
                return
            else:
                DoorPi().event_handler('OnCallReject', __name__)
                core.decline_call(call, linphone.Reason.Forbidden) #Declined
                DoorPi().event_handler('AfterCallReject', __name__)
                return
        elif call_state == linphone.CallState.OutgoingInit:
            pass
        elif call_state == linphone.CallState.OutgoingProgress:
            pass
        elif call_state == linphone.CallState.OutgoingRinging:
            pass
        elif call_state == linphone.CallState.OutgoingEarlyMedia:
            DoorPi().event_handler('OnCallMediaStateChange', __name__)
        elif call_state == linphone.CallState.Connected:
            DoorPi().event_handler('OnCallStateConnect', __name__)
        elif call_state == linphone.CallState.StreamsRunning:
            DoorPi().event_handler('AfterCallStateConnect', __name__)
            DoorPi().event_handler('OnCallMediaStateChange', __name__)
        elif call_state == linphone.CallState.Pausing:
            pass
        elif call_state == linphone.CallState.Paused:
            DoorPi().event_handler('OnCallMediaStateChange', __name__)
        elif call_state == linphone.CallState.Resuming:
            DoorPi().event_handler('OnCallStateConnect', __name__)
            DoorPi().event_handler('OnCallMediaStateChange', __name__)
        elif call_state == linphone.CallState.Refered:
            pass
        elif call_state == linphone.CallState.Error:
            if message == "Busy here": DoorPi().event_handler('OnCallStateDismissed', __name__)
        elif call_state == linphone.CallState.End:
            if message == "Call declined.": DoorPi().event_handler('OnCallStateReject', __name__)
            DoorPi().event_handler('OnCallStateDisconnect', __name__)
        elif call_state == linphone.CallState.PausedByRemote:
            pass
        elif call_state == linphone.CallState.UpdatedByRemote:
            pass
        elif call_state == linphone.CallState.IncomingEarlyMedia:
            DoorPi().event_handler('OnCallMediaStateChange', __name__)
        elif call_state == linphone.CallState.Updating:
            DoorPi().event_handler('OnCallStateConnect', __name__)
            DoorPi().event_handler('OnCallMediaStateChange', __name__)
        elif call_state == linphone.CallState.Released:
            pass
        elif call_state == linphone.CallState.EarlyUpdatedByRemote:
            pass
        elif call_state == linphone.CallState.EarlyUpdating:
            pass
    def notify_presence_received(self, core, linphone_friend): pass
    def new_subscription_requested(self, core, linphone_friend, url): pass
    def auth_info_requested(self, core, realm, username): pass
    def call_log_updated(self, core, new_call_log_entry): pass
    def message_received(self, core, linphone_chat_room, message): pass
    def is_composing_received(self, core, linphone_chat_room): pass
    def dtmf_received(self, core, call, digits):
        logger.debug("on_dtmf_digit (%s)", str(digits))
        digits = chr(digits)
        DoorPi().event_handler('OnDTMF', __name__, {'digits':digits})
        self.__DTMF += str(digits)
        for DTMF in self.__possible_DTMF:
            if self.__DTMF.endswith(DTMF[1:-1]):
                DoorPi().event_handler('OnDTMF_'+DTMF+'', __name__, {
                    'remote_uri': str(call.remote_address.as_string_uri_only()),
                    'DTMF': str(self.__DTMF)
                })
    def refer_received(self, core, refer_to): pass
    def call_encryption_changed(self, core, call, on, authentication_token): pass
    def transfer_state_changed(self, core, call, transfer_state): pass
    def buddy_info_updated(self, core, linphone_friend): pass
    def call_stats_updated(self, core, call, stats): pass
    def info_received(self, core, call, message): pass
    def subscription_state_changed(self, core, linphone_event, linphone_subscription_state): pass
    def notify_received(self, core, linphone_event, linphone_subscription_state, linphone_body): pass
    def configuring_status(self, core, linphone_configuring_state, message): pass
    def network_reachable(self, core, reachable): pass
    def log_collection_upload_state_changed(self, core, linphone_core_log_collection_upload_state, info): pass
    def log_collection_upload_progress_indication(self, core, offset, total): pass

    __del__ = destroy