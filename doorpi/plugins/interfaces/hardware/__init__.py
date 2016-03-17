# -*- coding: utf-8 -*-

from main import DOORPI
from plugins.interfaces import InterfaceBaseClass

logger = DOORPI.register_module(__name__, return_new_logger=True)


class SetOutputAction(DOORPI.events.action_base_class):
    pass


class HardwareInterfaceBaseClass(InterfaceBaseClass):
    _inputs = dict()
    _outputs = dict()

    _high_level = DOORPI.CONST.HIGH_LEVEL
    _low_level = DOORPI.CONST.LOW_LEVEL

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    def __init__(self, name, config_path):
        super(HardwareInterfaceBaseClass, self).__init__(name, config_path)

    def start(self):
        super(HardwareInterfaceBaseClass, self).start()
        if DOORPI.config(self._conf + '/reverse_polarity', False):
            self._high_level = DOORPI.CONST.LOW_LEVEL
            self._low_level = DOORPI.CONST.HIGH_LEVEL

    def stop(self):
        super(HardwareInterfaceBaseClass, self).stop()

    ############## methods to implement ##############
    # def status_input(self, input): raise NotImplementedError("Subclasses should implement this!")
    # def set_output(self, output, value, log = True): raise NotImplementedError("Subclasses should implement this!")
    ############ ############ ############ ############

    def status_output(self, output):
        return self._outputs[output]['value'] or None

    @property
    def active_inputs(self):
        active_inputs = []
        for input in self.inputs:
            if str(self.status_input(input)).lower() in self._low_level:
                active_inputs.append(input)
        return active_inputs

    @property
    def active_outputs(self):
        active_outputs = []
        for output in self.outputs:
            if str(self.status_output(output)).lower() in self._high_level:
                active_outputs.append(output)
        return active_outputs

    @property
    def first_active_input(self):
        return self.active_inputs.pop()

    @property
    def first_active_output(self):
        return self.active_outputs.pop()

    @property
    def input_name_variations(self):
        input_variations = dict()
        for input_id in self.inputs.keys():
            for interface_name in self.interface_name_variations(postfix='.'):
                input_variations["%s%s" % (interface_name, self.inputs[input_id].id)] = self.inputs[input_id].id
                input_variations["%s%s" % (interface_name, self.inputs[input_id].name)] = self.inputs[input_id].id
                input_variations["%s%s" % (interface_name, self.inputs[input_id].technical_name)] = self.inputs[
                    input_id].id
        return input_variations

    @property
    def output_name_variations(self):
        output_variations = dict()
        for output_id in self.outputs.keys():
            for interface_name in self.interface_name_variations(postfix='.'):
                output_variations["%s%s" % (interface_name, self.outputs[output_id].id)] = self.outputs[output_id].id
                output_variations["%s%s" % (interface_name, self.outputs[output_id].name)] = self.outputs[output_id].id
                output_variations["%s%s" % (interface_name, self.outputs[output_id].technical_name)] = self.outputs[
                    output_id].id
        return output_variations

    @property
    def channel_events(self, input_events=DOORPI.CONST.INTERFACES_HARDWARE_DEFAULT_INPUT_EVENTS,
                       output_events=DOORPI.CONST.INTERFACES_HARDWARE_DEFAULT_OUTPUT_EVENTS):
        possible_events = []
        for input_name in self.inputs.keys():
            possible_events = possible_events + self._create_event_variations(self.inputs[input_name].technical_name,
                                                                              input_events)
            possible_events = possible_events + self._create_event_variations(self.inputs[input_name].name,
                                                                              input_events)

        for output_name in self.outputs.keys():
            possible_events = possible_events + self._create_event_variations(self.outputs[output_name].technical_name,
                                                                              output_events)
            possible_events = possible_events + self._create_event_variations(self.outputs[output_name].name,
                                                                              output_events)

        return possible_events

    def _create_event_variations(self, channel, base_events):
        all_event_variations = []
        for event in base_events:
            for event_variations in [
                # OnInputActive
                "%s" % event,
                # mein_GPIO_Board.OnInputActive
                # "%s.%s"%(event, self.name),
                # plugins.interfaces.hardware.gpio.OnInputActive
                "%s.%s" % (self.module_name, event),
                # plugins.interfaces.hardware.gpio.mein_GPIO_Board.OnInputActive
                "%s.%s.%s" % (self.module_name, self.name, event),
                # 16.OnInputActive
                # "%s.%s"%(input, event),
                # mein_GPIO_Board.16.OnInputActive
                # "%s.%s.%s"%(self.name, input, event),
                # plugins.interfaces.hardware.gpio.16.OnInputActive
                # "%s.%s.%s"%(self.__class__.__module__, input, event),
                # plugins.interfaces.hardware.gpio.mein_GPIO_Board.16.OnInputActive
                "%s.%s.%s.%s" % (self.module_name, self.name, channel, event)
            ]:
                all_event_variations.append(event_variations)

        return all_event_variations

    def _register_outputs_actions(self):
        for output_id in self.outputs.keys():
            high_level_object = SetOutputAction(self.set_output,
                                                action='set_output',
                                                output=output_id,
                                                value=self.outputs[output_id].high_level,
                                                log=self.outputs[output_id].log,
                                                **self.interface_info
                                                )
            low_level_object = SetOutputAction(self.set_output,
                                               action='set_output',
                                               output=output_id,
                                               value=self.outputs[output_id].low_level,
                                               log=self.outputs[output_id].log,
                                               **self.interface_info
                                               )

            DOORPI.events.register_action(
                high_level_object,
                *self._create_event_variations(self.outputs[output_id].name,
                                               DOORPI.CONST.INTERFACES_HARDWARE_INCOMING_OUTPUT_EVENTS_HIGH)
            )
            DOORPI.events.register_action(
                low_level_object,
                *self._create_event_variations(self.outputs[output_id].name,
                                               DOORPI.CONST.INTERFACES_HARDWARE_INCOMING_OUTPUT_EVENTS_LOW)
            )

            if self.outputs[output_id].high_by_event:
                DOORPI.events.register_action(high_level_object, self.outputs[output_id].high_by_event)

            if self.outputs[output_id].low_by_event:
                DOORPI.events.register_action(low_level_object, self.outputs[output_id].low_by_event)
        return True

    def _register_channels(self):
        inputs = DOORPI.config(self._conf + '/inputs', [], function='keys')
        logger.info('%s has %s inputs', self.fullname, len(inputs))
        for input_name in inputs:
            if input_name in self._inputs: raise InputNameAlreadyExistsException()
            input_id = DOORPI.generate_id(prefix='Input_')
            self._inputs[input_id] = SingleChannel(
                id=input_id,
                name=input_name,
                technical_name=DOORPI.config('%s/inputs/%s/technical_name' % (self._conf, input_name), input_name),
                initial_value=DOORPI.config('%s/inputs/%s/initial_value' % (self._conf, input_name), False),
                log=DOORPI.config('%s/inputs/%s/log' % (self._conf, input_name), True),
            )

        outputs = DOORPI.config(self._conf + '/outputs', [], function='keys')
        logger.info('%s has %s outputs', self.fullname, len(outputs))
        for output_name in outputs:
            if output_name in self._outputs: raise OutputNameAlreadyExistsException()
            output_id = DOORPI.generate_id(prefix='Output_')
            self._outputs[output_id] = SingleChannel(
                id=output_id,
                name=output_name,
                technical_name=DOORPI.config('%s/outputs/%s/technical_name' % (self._conf, output_name), output_name),
                initial_value=DOORPI.config('%s/outputs/%s/initial_value' % (self._conf, output_name), False),
                log=DOORPI.config('%s/outputs/%s/log' % (self._conf, output_name), True),
                high_level=DOORPI.config('%s/outputs/%s/high_level' % (self._conf, output_name), True),
                low_level=DOORPI.config('%s/outputs/%s/low_level' % (self._conf, output_name), False),
                high_by_event=DOORPI.config('%s/outputs/%s/high_by_event' % (self._conf, output_name), None),
                low_by_event=DOORPI.config('%s/outputs/%s/low_by_event' % (self._conf, output_name), None),
            )

    # TODO: Name gleichziehen wie unten _fire_events_for_input_id
    def _fire_output_event(self, technical_name, event_names):
        for output_id in self.outputs:
            if self.outputs[output_id].technical_name != technical_name: continue
            for event_variation in self._create_event_variations(self.outputs[output_id].technical_name, event_names):
                DOORPI.events(self._id, event_variation,
                              kwargs=self.inputs[input_id].__dict__.update(self.interface_info))
            for event_variation in self._create_event_variations(self.outputs[output_id].name, event_names):
                DOORPI.events(self._id, event_variation,
                              kwargs=self.inputs[input_id].__dict__.update(self.interface_info))
            return True
        return False

    def _fire_events_for_input_id(self, event_names, input_id):
        if input_id not in self.inputs: return False
        for event_variation in self._create_event_variations(self.inputs[input_id].technical_name, event_names):
            DOORPI.events(self._id, event_variation, kwargs=self.inputs[input_id].__dict__.update(self.interface_info))
        for event_variation in self._create_event_variations(self.inputs[input_id].name, event_names):
            DOORPI.events(self._id, event_variation, kwargs=self.inputs[input_id].__dict__.update(self.interface_info))
        return True

    def get_input_id_by_technical_name(self, technical_name):
        for input_id in self.inputs:
            if self.inputs[input_id].technical_name == technical_name:
                return input_id
        return None

    def get_output_id_by_technical_name(self, technical_name):
        for output_id in self.outputs:
            if self.outputs[output_id].technical_name == technical_name:
                return output_id
        return None


class SingleChannel(object):
    actions = []

    def __init__(self, id, name, technical_name, initial_value=False, log=True, high_level=True,
                 low_level=False, high_by_event=None, low_by_event=None, direction="input"):
        self.id = id
        self.name = name
        self.technical_name = technical_name
        self.value = initial_value
        self.initial_value = initial_value
        self.log = log
        self.high_level = high_level
        self.low_level = low_level
        self.high_by_event = high_by_event
        self.low_by_event = low_by_event
        self.direction = direction
