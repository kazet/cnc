import time
import RPi.GPIO


class RaspberryPiGPIOMotorDriver:
    def __init__(self, motor_pins, is_inverse=False):
        self._is_inverse = is_inverse
        self._motor_pins = motor_pins

        self._configure_gpio()

    def signal_go_left(self):
        self._output(
            self._motor_pins['DIR'],
            0 if self._is_inverse else 1
        )

    def signal_go_right(self):
        self._output(
            self._motor_pins['DIR'],
            1 if self._is_inverse else 0
        )

    def signal_pul_up(self):
        self._output(
            self._motor_pins['PUL'],
            1
        )

    def signal_pul_down(self):
        self._output(
            self._motor_pins['PUL'],
            0
        )

    def step_left(self, step_time):
        self.signal_go_left()
        self.step(step_time)

    def step_right(self, step_time):
        self.signal_go_right()
        self.step(step_time)

    def step(self, step_time):
        self.signal_pul_up()
        time.sleep(step_time / 2.0)
        self.signal_pul_down()
        time.sleep(step_time / 2.0)

    def _configure_gpio(self):
        RPi.GPIO.setmode(RPi.GPIO.BOARD)

        for motor_pin in self._motor_pins.values():
            RPi.GPIO.setup(motor_pin, RPi.GPIO.OUT)

    def _output(self, pin, value):
        RPi.GPIO.output(pin, value)
