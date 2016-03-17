# -*- coding: utf-8 -*-

from main import DOORPI
import RPi.GPIO as GPIO  # basic for GPIO control
from plugins.interfaces.hardware import HardwareInterfaceBaseClass, UnknownInputException, UnknownOutputException, \
    UnknownLevelException

logger = DOORPI.register_module(__name__, return_new_logger=True)


class GPIOBasedInterface(HardwareInterfaceBaseClass):
    def __init__(self, name, config_path):
        super(GPIOBasedInterface, self).__init__(name, config_path)

    def start(self):
        super(GPIOBasedInterface, self).start()

        GPIO.setwarnings(DOORPI.config(self._conf + '/setwarnings', False))
        GPIO.setmode(DOORPI.config(self._conf + '/mode', GPIO.BOARD))

        logger.debug('use GPIO %s - %s', GPIO.VERSION, GPIO.RPI_INFO)

        self._register_channels()

        DOORPI.events.register_events(self.module_name, *self.channel_events)

        default_edge = DOORPI.config('%s/event_edge' % self._conf, GPIO.BOTH)
        default_bouncetime = DOORPI.config('%s/event_bouncetime' % self._conf, 40)
        default_pull_up_down = DOORPI.config('%s/pull_up_down' % self._conf, GPIO.PUD_OFF)

        for input_id in self.inputs:
            GPIO.setup(
                channel=self.inputs[input_id].technical_name,
                direction=GPIO.IN,
                pull_up_down=DOORPI.config('%s/outputs/%s/pull_up_down' % (self._conf, self.inputs[input_id].name),
                                           default_pull_up_down)
            )
            GPIO.add_event_detect(
                gpio=self.inputs[input_id].technical_name,
                edge=DOORPI.config('%s/outputs/%s/event_edge' % (self._conf, self.inputs[input_id].name), default_edge),
                callback=self.event_detect,
                bouncetime=DOORPI.config('%s/outputs/%s/event_bouncetime' % (self._conf, self.inputs[input_id].name),
                                         default_bouncetime)
            )

        for output_id in self.outputs:
            GPIO.setup(
                channel=self.outputs[output_id].technical_name,
                direction=GPIO.OUT,
                initial=self.outputs[output_id].value
            )
            self.set_output(output_id, self.outputs[output_id].value, log=False)

        self._register_outputs_actions()

    def stop(self):
        super(GPIOBasedInterface, self).stop()
        for input_id in self.inputs:
            GPIO.remove_event_detect(self.inputs[input_id].technical_name)
        GPIO.cleanup()

    def status_input(self, technical_name):
        return GPIO.input(technical_name)

    def event_detect(self, technical_name):
        if str(technical_name) not in self.input_name_variations: raise UnknownInputException()
        input_id = self.input_name_variations[str(technical_name)]
        self.inputs[input_id].value = self.status_input(technical_name)
        if self.inputs[input_id].value:
            self._fire_events_for_input_id(['OnInputActive', 'OnInputChange'], input_id)
        else:
            self._fire_events_for_input_id(['OnInputInactive', 'OnInputChange'], input_id)

    def set_output(self, output, value, log=True):
        if str(output) not in self.output_name_variations: raise UnknownOutputException()
        output_id = self.output_name_variations[str(output)]

        if value in self._high_level:
            value = True
        elif value in self._low_level:
            value = False
        self.outputs[output_id].value = value

        if log: logger.debug("out(pin = %s, value = %s, log_output = %s)", output_id, value, log)
        GPIO.output(self.outputs[output_id].technical_name, value)
        return True


__interface__ = GPIOBasedInterface
