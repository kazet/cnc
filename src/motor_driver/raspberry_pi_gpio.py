import time
import RPi.GPIO


class RaspberryPiGPIOMotorDriver:
    MOTOR_PINS = {
        'X': {
            'DIR': 35,
            'PUL': 37,
        },
        'Y': {
            'DIR': 33,
            'PUL': 31,
        },
        'Z': {
            'DIR': 36,
            'PUL': 38,
        },
    }

    def __init__(self, axis, is_inverse=False):
        self._axis = axis
        self._is_inverse = is_inverse

        self._configure_gpio()

    def signal_go_left(self):
        self._output(
            self.MOTOR_PINS[self._axis]['DIR'],
            0 if self._is_inverse else 1
        )

    def signal_go_right(self):
        self._output(
            self.MOTOR_PINS[self._axis]['DIR'],
            1 if self._is_inverse else 0
        )

    def signal_pul_up(self):
        self._output(
            self.MOTOR_PINS[self._axis]['PUL'],
            1
        )

    def signal_pul_down(self):
        self._output(
            self.MOTOR_PINS[self._axis]['PUL'],
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

        for motor_pin_dict in self.MOTOR_PINS.values():
            for output_pin_id in motor_pin_dict.values():
                RPi.GPIO.setup(output_pin_id, RPi.GPIO.OUT)

    def _output(self, pin, value):
        RPi.GPIO.output(pin, value)
