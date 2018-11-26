import time

class MotorDriver:
    def __init__(self, mill_pin_driver, axis, is_inverse=False):
        self._mill_pin_driver = mill_pin_driver
        self._axis = axis
        self._is_inverse = is_inverse

    def signal_go_left(self):
        self._mill_pin_driver.output(
            self._mill_pin_driver.MOTOR_PINS[self._axis]['DIR'],
            0 if self._is_inverse else 1
        )

    def signal_go_right(self):
        self._mill_pin_driver.output(
            self._mill_pin_driver.MOTOR_PINS[self._axis]['DIR'],
            1 if self._is_inverse else 0
        )

    def signal_pul_up(self):
        self._mill_pin_driver.output(
            self._mill_pin_driver.MOTOR_PINS[self._axis]['PUL'],
            1
        )

    def signal_pul_down(self):
        self._mill_pin_driver.output(
            self._mill_pin_driver.MOTOR_PINS[self._axis]['PUL'],
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
