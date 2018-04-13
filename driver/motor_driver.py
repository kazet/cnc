import time

class MotorDriver:
    def __init__(self, mill_pin_driver, axis):
        self._mill_pin_driver = mill_pin_driver
        self._axis = axis

    def signal_go_left(self):
        self._mill_pin_driver.output(
            self._mill_pin_driver.MOTOR_PINS[self._axis]['DIR'],
            1
        )

    def signal_go_right(self):
        self._mill_pin_driver.output(
            self._mill_pin_driver.MOTOR_PINS[self._axis]['DIR'],
            0
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
        self.signal_pul_up()
        time.sleep(step_time / 2.0)
        self.signal_pul_down()
        time.sleep(step_time / 2.0)

    def step_right(self, step_time):
        self.signal_go_right()
        self.signal_pul_up()
        time.sleep(step_time / 2.0)
        self.signal_pul_down()
        time.sleep(step_time / 2.0)
