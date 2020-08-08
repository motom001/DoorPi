import logging
import RPi.GPIO as gpio  # pylint: disable=import-error

from doorpi import keyboard

from .abc import AbstractKeyboard

LOGGER = logging.getLogger(__name__)
INSTANTIATED = False


class GPIOKeyboard(AbstractKeyboard):

    def __init__(self, name):
        # pylint: disable=no-member  # Only available at runtime
        global INSTANTIATED
        if INSTANTIATED:
            raise RuntimeError("Only one GPIO keyboard may be instantiated")
        INSTANTIATED = True

        super().__init__(name)

        gpio.setwarnings(False)

        gpio.setmode((gpio.BOARD, gpio.BCM)[self.config["mode"].value - 1])

        pull = self.config["pull_up_down"]
        if pull is keyboard.PullUpDown.OFF:
            pull = gpio.PUD_OFF
        elif pull is keyboard.PullUpDown.UP:
            pull = gpio.PUD_UP
        elif pull is keyboard.PullUpDown.DOWN:
            pull = gpio.PUD_DOWN
        else:
            raise ValueError(f"{self.name}: Invalid pull_up_down value")

        gpio.setup(self._inputs, gpio.IN, pull_up_down=pull)
        for input_pin in self._inputs:
            gpio.add_event_detect(
                input_pin, gpio.BOTH, callback=self.event_detect,
                bouncetime=int(self._bouncetime))

        gpio.setup(self._outputs.keys(), gpio.OUT)
        for output_pin in self._outputs:
            self.output(output_pin, False)

    def destroy(self):
        global INSTANTIATED

        for pin in self._outputs:
            self.output(pin, False)
        gpio.cleanup()
        INSTANTIATED = False
        super().destroy()

    def event_detect(self, pin):
        """Callback for detected GPIO events."""
        if self.input(pin):
            self._fire_keydown(pin)
        else:
            self._fire_keyup(pin)

    def input(self, pin):
        super().input(pin)
        pin = int(pin)
        return self._normalize(gpio.input(pin))

    def output(self, pin, value):
        super().output(pin, value)
        pin = int(pin)
        value = self._normalize(value)
        gpio.output(pin, value)
        self._outputs[pin] = value
        return True


instantiate = GPIOKeyboard  # pylint: disable=invalid-name
