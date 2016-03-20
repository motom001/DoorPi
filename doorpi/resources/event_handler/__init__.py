# -*- coding: utf-8 -*-

import threading
import time
from inspect import isfunction, ismethod
import importlib
import datetime

from main import DOORPI
from resources.event_handler.classes import ActionBaseClass, EventBaseClass

logger = DOORPI.register_module(__name__, return_new_logger=True)

# from resources.event_handler.docs import DOCUMENTATION as EVENT_HANDLER_DOCUMENTATION
# from resources.event_handler.time_tick import TimeTicker


class ControlPulseAction(ActionBaseClass):
    pass


class LogRealTimeAction(ActionBaseClass):
    pass


class MissingEventDocumentationException(Exception):
    pass


class EventHandler:
    _conf = []
    _history = None

    _events = {}  # Auflistung aller Event - Key ist EventName
    _actions = {}  # Auflistung aller Actions - Key ist action id

    _destroy = False

    _last_heart_beat = 1
    _last_time_tick = 0
    _last_realtime_event = 0

    @property
    def events(self):
        return self._events

    @property
    def actions(self):
        return self._actions

    @property
    def action_base_class(self):
        return ActionBaseClass

    @property
    def pulse(self):
        return 1 / self._last_heart_beat

    @property
    def threads(self):
        return threading.enumerate()

    @property
    def idle(self):
        return len(self.threads) - 1 is 0

    def __init__(self):
        DOORPI.register_module(__name__, self.start, self.stop, False)

    def start(self):
        logger.debug(_("start EventHandler"))
        # self._conf = DOORPI.config.get_modul_config(__name__)
        # self._history = EventHistoryHandler().start(
        #    db_type =           DOORPI.config('/resources/event_handler/event_log/type', 'sqlite'),
        #    connection_string = DOORPI.config('/resources/event_handler/event_log/connection_string', '!BASE_PATH!/conf/event_log.db'),
        # )

        DOORPI.events.register_events(__name__)
        DOORPI.events.register_action(ControlPulseAction(self.control_pulse), 'OnTimeSecond')
        #DOORPI.events.register_action(LogRealTimeAction(self.log_realtime_event), 'OnTimeTick')
        self._last_time_tick = time.time()
        return self

    def log_realtime_event(self):
        logger.debug(_('real time event fired'))

    def control_pulse(self):
        if self._destroy:
            return
        if DOORPI.CONST.HEART_BEAT_LEVEL_CRITICAL and self.pulse < DOORPI.CONST.HEART_BEAT_LEVEL_CRITICAL:
            logger.critical(_('DoorPi pulse is %s'), self.pulse)
        elif DOORPI.CONST.HEART_BEAT_LEVEL_ERROR and self.pulse < DOORPI.CONST.HEART_BEAT_LEVEL_ERROR:
            logger.error(_('DoorPi pulse is %s'), self.pulse)
        elif DOORPI.CONST.HEART_BEAT_LEVEL_WARNING and self.pulse < DOORPI.CONST.HEART_BEAT_LEVEL_WARNING:
            logger.warning(_('DoorPi pulse is %s'), self.pulse)
        elif DOORPI.CONST.HEART_BEAT_LEVEL_INFO and self.pulse < DOORPI.CONST.HEART_BEAT_LEVEL_INFO:
            logger.info(_('DoorPi pulse is %s'), self.pulse)
        elif DOORPI.CONST.HEART_BEAT_LEVEL_DEBUG and self.pulse < DOORPI.CONST.HEART_BEAT_LEVEL_DEBUG:
            logger.debug(_('DoorPi pulse is %s'), self.pulse)

    def stop(self):
        logger.info(_('stop event handler'))
        self._destroy = True
        self._history.stop()
        return self

    def heart_beat(self):

        timestamp_now = time.time()
        timestamp_past = self._last_time_tick
        datetime_now = datetime.datetime.fromtimestamp(timestamp_now)
        datetime_past = datetime.datetime.fromtimestamp(timestamp_past)

        past_dict = dict(
            year=datetime_past.year,
            month=datetime_past.month,
            day=datetime_past.day,
            hour=datetime_past.hour,
            minute=datetime_past.minute,
            second=datetime_past.second
        )
        now_dict = dict(
            year=datetime_now.year,
            month=datetime_now.month,
            day=datetime_now.day,
            hour=datetime_now.hour,
            minute=datetime_now.minute,
            second=datetime_now.second
        )

        for datetime_part in DOORPI.CONST.DATETIME_PARTS:
            if now_dict[datetime_part] != past_dict[datetime_part]:
                self('OnTime%s' % datetime_part.capitalize(), __name__, kwargs=now_dict)
                if now_dict[datetime_part] % 2 is 0:
                    self('OnTime%sEvenNumber' % datetime_part.capitalize(), __name__, kwargs=now_dict)
                else:
                    self('OnTime%sUnevenNumber' % datetime_part.capitalize(), __name__, kwargs=now_dict)

                if datetime_part == "Hour" and now_dict[datetime_part] in DOORPI.CONST.HOUR_RANGE:
                    self('OnTimeHour%s' % now_dict[datetime_part], __name__, kwargs=now_dict)

                if datetime_part == "Minute" and now_dict[datetime_part] in DOORPI.CONST.MINUTE_RANGE:
                    self('OnTimeMinute%s' % now_dict[datetime_part], __name__, kwargs=now_dict)

        microsecond = datetime_now.microsecond / 100000
        if (microsecond % 2 is 0 or microsecond is 0) and microsecond is not self._last_realtime_event:
            self._last_realtime_event = microsecond
            DOORPI.events('OnTimeTick', __name__, kwargs=now_dict)

        sleep_time = (self._last_heart_beat * 0.5 + DOORPI.CONST.HEART_BEAT_BASE_VALUE) - (timestamp_now - time.time())
        if sleep_time > 0:
            time.sleep(sleep_time)

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
        return sorted(event_list)

    def get_actions_for_source(self, source_name):
        action_list = []
        for action_id in self._actions.keys():
            if source_name in self._actions[action_id].module:
                action_list.append(action_id.name)
        return sorted(action_list)

    def _register_event(self, module_name, event_name):
        if event_name not in self._events.keys():
            self._events[event_name] = EventBaseClass(
                event_name=event_name
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
            logger.debug(_('%s has now %s events: %s'),
                         module_name,
                         len(self.get_events_for_source(module_name)),
                         self.get_events_for_source(module_name))
        return True

    def get_event_default_parameters(self, event_name, event_source):
        module_documentation = DOORPI.config.get_module_documentation_by_module_name(event_source)
        for event_dict in module_documentation['events']:
            if event_dict['name'] != event_name:
                continue
            if 'parameter' in event_dict:
                return event_dict['parameter']
        return []

    def unregister_event(self, event_name, event_source):
        if event_name not in self._events:
            return False
        if event_source not in self._events[event_name].sources:
            return False

        self._events[event_name].sources.remove(event_source)

        if len(self._events[event_name].sources) == 0 and len(self._events[event_name].actions) == 0:
            logger.debug(_('remove event %s because there are no more sources and actions for this event'), event_name)
            del self._events[event_name]

        return True

    def unregister_source(self, event_source):
        # for action_id in self._actions.keys():
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
                logger.debug(_("action_object: %s"), action_object)
                action_object = ActionBaseClass(
                    callback=importlib.import_module("plugins.actions.%s" % action_object['action']).__action__,
                    id=action_object['name'],
                    kwargs={} if 'parameters' not in action_object else action_object['parameters']
                )
            except Exception as exp:
                logger.exception(_('failed to create action_object from config (%s)'), exp)
                return False

        self._actions[action_object.id] = action_object

        for event_name in event_names:
            self._register_event(None, event_name)
            if action_object.id not in self._events[event_name].actions:
                self._events[event_name].actions.append(action_object.id)
                logger.debug(_("action '%s' was added to event %s"), str(action_object), event_name)

        return action_object

    def unregister_action(self, action_id):
        if action_id not in self._actions:
            return False
        action_name = self._actions[action_id].name
        for event_name in self._events.keys():
            if action_id in self._events[event_name].actions:
                logger.debug(_('[%s] remove action %s from event %s'), action_id, action_name, event_name)
                del self._events[event_name].actions[action_id]
        logger.debug(_('[%s] remove action %s'), action_id, action_name)
        del self._actions[action_id]
        return True

    def fire_event(self, event_name, event_source, syncron=False, kwargs=None):
        if syncron is False:
            return self.fire_event_asynchron(event_source, event_name, kwargs)
        else:
            return self.fire_event_synchron(event_source, event_name, kwargs)

    def fire_event_asynchron(self, event_source, event_name, kwargs=None):
        return threading.Thread(
            target=self.fire_event_synchron,
            args=(event_name, event_source, kwargs),
            name=_("%s from %s with kwargs %s") % (event_source, event_name, kwargs)
        ).start()

    def fire_event_synchron(self, event_source, event_name, kwargs=None):
        if self._destroy and event_source != __name__:
            return False
        log = self.log_for_event(event_name)

        event_fire_id = DOORPI.generate_id(prefix='Event_')

        if kwargs is None:
            kwargs = {}
        kwargs.update({
            'last_fired': time.time(),
            'last_fired_from': event_source,
            'event_fire_id': event_fire_id
        })

        message = ''
        if event_name not in self._events.keys():
            message = _('unknown event')
        elif event_source not in self._events[event_name].sources:
            message = _('unknown source for this event')
        elif len(self._events[event_name].actions) == 0:
            message = _('no actions for this event')
        if message != '':
            message = _('[%s] %s - skip fire event %s from %s') % (event_fire_id, message, event_name, event_source)
            if log:
                logger.info(message)
            return message

        if log:
            logger.debug(_("[%s] fire for event %s from %s this actions %s with kwargs %s"),
                         event_fire_id, event_name, event_source, self._events[event_name].actions, kwargs)

        for action_id in self._events[event_name].actions:
            if action_id not in self._actions.keys():
                logger.error(_('[%s] missing action reference for action_id %s by event %s'), event_fire_id, action_id,
                             event_name)
                continue
            if log:
                logger.debug(_("[%s] try to fire action %s"), event_fire_id, self._actions[action_id])
            try:
                result = self._actions[action_id].run(**kwargs)
                if not result and log:
                    logger.warning(_('[%s] action %s returns %s'), event_fire_id, self._actions[action_id], result)
                if self._actions[action_id].single_fire_action is True:
                    self.unregister_action(action_id)
            except SystemExit as exp:
                logger.info(_('[%s] Detected SystemExit and shutdown DoorPi (Message: %s)'), event_fire_id, exp)
                DOORPI.stop()
            except KeyboardInterrupt as exp:
                logger.info(_("[%s] Detected KeyboardInterrupt and shutdown DoorPi (Message: %s)"), event_fire_id, exp)
                DOORPI.stop()
            except Exception as exp:
                logger.exception(_("[%s] error while fire action %s for event_name %s: %s"), event_fire_id,
                                 self._actions[action_id], event_name, exp)
        if log:
            logger.debug(_("[%s] finished fire_event for event %s from %s"), event_fire_id, event_name, event_source)
        return True

    __call__ = fire_event_asynchron
