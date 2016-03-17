# -*- coding: utf-8 -*-

import threading
import time # used by: fire_event_synchron
from inspect import isfunction, ismethod # used by: register_action
import importlib
import datetime

from main import DOORPI
logger = DOORPI.register_module(__name__, return_new_logger = True)

#from resources.event_handler.docs import DOCUMENTATION as EVENT_HANDLER_DOCUMENTATION
from resources.event_handler.classes import ActionBaseClass, EventBaseClass
#from resources.event_handler.time_tick import TimeTicker

class ControlPulseAction(ActionBaseClass): pass
class LogRealtimeAction(ActionBaseClass): pass
class MissingEventDocumentationException(Exception): pass

class EventHandler:

    _conf = []
    _history = None

    _events = {}  # Auflistung aller Event - Key ist EventName
    _actions = {} # Auflistung aller Actions - Key ist action id

    _destroy = False

    _last_heart_beat = 1
    _last_time_tick = 0
    _last_realtime_event = 0

    @property
    def events(self): return self._events
    @property
    def actions(self): return self._actions
    @property
    def action_base_class(self): return ActionBaseClass
    @property
    def pulse(self): return 1 / self._last_heart_beat
    @property
    def threads(self): return threading.enumerate()
    @property
    def idle(self): return len(self.threads) - 1 is 0

    def __init__(self):
        DOORPI.register_module(__name__, self.start, self.stop, False)

    def start(self):
        logger.debug("start EventHandler")
        #self._conf = DOORPI.config.get_modul_config(__name__)
        #self._history = EventHistoryHandler().start(
        #    db_type =           DOORPI.config('/resources/event_handler/event_log/type', 'sqlite'),
        #    connection_string = DOORPI.config('/resources/event_handler/event_log/connection_string', '!BASE_PATH!/conf/event_log.db'),
        #)

        DOORPI.events.register_events(__name__)
        DOORPI.events.register_action(ControlPulseAction(self.control_pulse), 'OnTimeSecond')
        #DOORPI.events.register_action(LogRealtimeAction(self.log_realtime_event), 'OnTimeTick')
        return self

    def log_realtime_event(self):
        logger.debug('realtime event fired')

    def control_pulse(self):
        if self._destroy: return
        if DOORPI.CONST.HEART_BEAT_LEVEL_CRITICAL and self.pulse  < DOORPI.CONST.HEART_BEAT_LEVEL_CRITICAL: logger.critical('DoorPi pulse is %s', self.pulse)
        elif DOORPI.CONST.HEART_BEAT_LEVEL_ERROR and self.pulse   < DOORPI.CONST.HEART_BEAT_LEVEL_ERROR:    logger.error('DoorPi pulse is %s', self.pulse)
        elif DOORPI.CONST.HEART_BEAT_LEVEL_WARNING and self.pulse < DOORPI.CONST.HEART_BEAT_LEVEL_WARNING:  logger.warning('DoorPi pulse is %s', self.pulse)
        elif DOORPI.CONST.HEART_BEAT_LEVEL_INFO and self.pulse    < DOORPI.CONST.HEART_BEAT_LEVEL_INFO:     logger.info('DoorPi pulse is %s', self.pulse)
        elif DOORPI.CONST.HEART_BEAT_LEVEL_DEBUG and self.pulse   < DOORPI.CONST.HEART_BEAT_LEVEL_DEBUG:    logger.debug('DoorPi pulse is %s', self.pulse)

    def stop(self):
        logger.info('stop event handler')
        self._destroy = True
        self._history.stop()
        return self

    def heart_beat(self):

        timestamp_now = time.time()
        timestamp_past = self._last_time_tick

        datetime_now = datetime.datetime.fromtimestamp(timestamp_now)
        datetime_past = datetime.datetime.fromtimestamp(timestamp_past)

        if datetime_now.year != datetime_past.year:
            DOORPI.events('OnTimeYear', __name__)
            if datetime_now.year % 2 is 0:      self('OnTimeYearEvenNumber', __name__)
            else:                               self('OnTimeYearUnevenNumber', __name__)

        if datetime_now.month != datetime_past.month:
            DOORPI.events('OnTimeMonth', __name__)
            if datetime_now.month % 2 is 0:     self('OnTimeMonthEvenNumber', __name__)
            else:                               self('OnTimeMonthUnevenNumber', __name__)

        if datetime_now.day != datetime_past.day:
            DOORPI.events('OnTimeDay', __name__)
            if datetime_now.day % 2 is 0:       self('OnTimeDayEvenNumber', __name__)
            else:                               self('OnTimeDayUnevenNumber', __name__)

        if datetime_now.hour != datetime_past.hour:
            DOORPI.events('OnTimeHour', __name__)
            if datetime_now.hour % 2 is 0:      self('OnTimeHourEvenNumber', __name__)
            else:                               self('OnTimeHourUnevenNumber', __name__)

            for hour in DOORPI.CONST.HOUR_RANGE:
                if hour is datetime_now.hour:   self('OnTimeHour%s'%hour, __name__)

        if datetime_now.minute != datetime_past.minute:
            DOORPI.events('OnTimeMinute', __name__)
            if datetime_now.minute % 2 is 0:    self('OnTimeMinuteEvenNumber', __name__)
            else:                               self('OnTimeMinuteUnevenNumber', __name__)

            for minute in DOORPI.CONST.MINUTE_RANGE:
                if minute is datetime_now.minute: self('OnTimeMinute%s'%minute, __name__)

            if datetime_now.minute % 5 is 0:    self('OnTimeMinuteEvery5', __name__)

        if datetime_now.second != datetime_past.second:
            DOORPI.events('OnTimeSecond', __name__)
            if datetime_now.second % 2 is 0:    self('OnTimeSecondEvenNumber', __name__)
            else:                               self('OnTimeSecondUnevenNumber', __name__)

        microsecond = datetime_now.microsecond / 100000
        if (microsecond % 2 is 0 or microsecond is 0) and microsecond is not self._last_realtime_event:
            self._last_realtime_event = microsecond
            DOORPI.events('OnTimeTick', __name__)

        sleep_time = (self._last_heart_beat * 0.5 + DOORPI.CONST.HEART_BEAT_BASE_VALUE) - (timestamp_now - time.time())
        if sleep_time > 0: time.sleep(sleep_time)

        self._last_time_tick = timestamp_now
        self._last_heart_beat = time.time() - timestamp_now
        return not self._destroy

    def log_for_event(self, event_name):
        return 'OnTime' not in event_name

    def get_events_for_source(self, source_name):
        event_list = []
        for event_name in self._events.keys():
            if source_name in self._events[event_name].sources:
                event_list.append(event_name)
        return event_list

    def get_actions_for_source(self, source_name):
        action_list = []
        for action_id in self._actions.keys():
            if source_name in self._actions[action_id].module:
                action_list.append(action_id.name)
        return action_list

    def _register_event(self, module_name, event_name):
        if event_name not in self._events.keys():
            self._events[event_name] = EventBaseClass(
                event_name = event_name
            )

        if module_name and module_name not in self._events[event_name].sources:
            self._events[event_name].sources.append(module_name)

        return True

    def register_events(self, module_name, *event_names):
        try:
            module_documentation = DOORPI.config.get_module_documentation_by_module_name(module_name)
            for event_dict in module_documentation['events']:
                self._register_event(module_name, event_dict['name'])
        except:
            pass

        for event_name in event_names:
            self._register_event(module_name, event_name)

        if module_name is not None:
            logger.debug('%s has now %s events: %s', module_name, len(self.get_events_for_source(module_name)), self.get_events_for_source(module_name))
        return True

    def get_event_default_parameters(self, event_name, event_source):
        module_documentation = DOORPI.config.get_module_documentation_by_module_name(event_source)
        for event_dict in module_documentation['events']:
            if event_dict['name'] != event_name: continue
            if 'parameter' in event_dict:
                return event_dict['parameter']
        return []

    def unregister_event(self, event_name, event_source):
        if event_name not in self._events: return False
        if event_source not in self._events[event_name].sources: return False

        self._events[event_name].sources.remove(event_source)

        if len(self._events[event_name].sources) == 0 and len(self._events[event_name].actions) == 0:
            logger.debug('remove event %s because there are no more sources and actions for this event', event_name)
            del self._events[event_name]

        return True

    def unregister_source(self, event_source):
        #for action_id in self._actions.keys():
        #    if event_source == self._actions[action_id]:
        #        self.unregister_action(action_id)
        for event_name in self._events.keys():
            self.unregister_event(event_name, event_source)
        return True

    def register_action(self, action_object, *event_names, **kwargs):
        if isinstance(action_object, ActionBaseClass):
            action_object = action_object
        elif callable(action_object) and (ismethod(action_object) or isfunction(action_object)):
            action_object = ActionBaseClass(action_object, **kwargs)
        else:
            try:
                logger.debug("action_object: %s", action_object)
                action_object = ActionBaseClass(
                    callback = importlib.import_module("plugins.actions.%s"%action_object['action']).__action__,
                    id = action_object['name'],
                    kwargs = {} if 'parameters' not in action_object else action_object['parameters']
                )
            except Exception as exp:
                logger.exception('failed to create action_object from config (%s)', exp)
                return False

        self._actions[action_object.id] = action_object


        for event_name in event_names:
            self._register_event(None, event_name)
            if action_object.id not in self._events[event_name].actions:
                self._events[event_name].actions.append(action_object.id)
                logger.debug("action '%s' was added to event %s", str(action_object), event_name)

        return action_object

    def unregister_action(self, action_id):
        if action_id not in self._actions: return False
        action_name = self._actions[action_id].name
        for event_name in self._events.keys():
            if action_id in self._events[event_name].actions:
                logger.debug('[%s] remove action %s from event %s', action_id, action_name, event_name)
                del self._events[event_name].actions[action_id]
        logger.debug('[%s] remove action %s', action_id, action_name)
        del self._actions[action_id]
        return True

    def fire_event(self, event_name, event_source, syncron = False, kwargs = None):
        if syncron is False: return self.fire_event_asynchron(event_source, event_name, kwargs)
        else: return self.fire_event_synchron(event_source, event_name, kwargs)

    def fire_event_asynchron(self, event_source, event_name, kwargs = None):
        return threading.Thread(
            target = self.fire_event_synchron,
            args = (event_name, event_source, kwargs),
            name = "%s from %s with kwargs %s" % (event_source, event_name, kwargs)
        ).start()

    def fire_event_synchron(self, event_source, event_name, kwargs = None):
        if self._destroy and event_source != __name__: return False
        log = self.log_for_event(event_name)

        event_fire_id = DOORPI.generate_id(prefix = 'Event_')

        if kwargs is None: kwargs = {}
        kwargs.update({
            'last_fired': time.time(),
            'last_fired_from': event_source,
            'event_fire_id': event_fire_id
        })

        message = ''
        if event_name not in self._events.keys():                     message = 'unknown event'
        elif event_source not in self._events[event_name].sources:    message = 'unknown source for this event'
        elif len(self._events[event_name].actions) == 0:              message = 'no actions for this event'
        if message != '':
            message = '[%s] %s - skip fire event %s from %s'%(event_fire_id, message, event_name, event_source)
            if log: logger.info(message)
            return message

        if log: logger.debug("[%s] fire for event %s from %s this actions %s with kwargs %s",
                             event_fire_id, event_name, event_source, self._events[event_name].actions, kwargs)

        for action_id in self._events[event_name].actions:
            if action_id not in self._actions.keys():
                logger.error('[%s] missing action reference for action_id %s by event %s', event_fire_id, action_id, event_name)
                continue
            if log: logger.debug("[%s] try to fire action %s", event_fire_id, self._actions[action_id])
            try:
                result = self._actions[action_id].run(**kwargs)
                if not result and log: logger.warning('[%s] action %s returns %s', event_fire_id, self._actions[action_id], result)
                if self._actions[action_id].single_fire_action is True: self.unregister_action(action_id)
            except SystemExit as exp:
                logger.info('[%s] Detected SystemExit and shutdown DoorPi (Message: %s)', event_fire_id, exp)
                DOORPI.stop()
            except KeyboardInterrupt as exp:
                logger.info("[%s] Detected KeyboardInterrupt and shutdown DoorPi (Message: %s)", event_fire_id, exp)
                DOORPI.stop()
            except:
                logger.exception("[%s] error while fire action %s for event_name %s", event_fire_id, self._actions[action_id], event_name)
        if log: logger.debug("[%s] finished fire_event for event %s from %s", event_fire_id, event_name, event_source)
        return True


    __call__ = fire_event_asynchron


