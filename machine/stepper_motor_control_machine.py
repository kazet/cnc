import math

from steps_sequence import create_xyz_steps_sequence


class MachineUseException(Exception):
    def __init__(self, message):
        self.message = message
        

class MachineAxis:
    def __init__(self, motor, backlash, mm_per_revolution, steps_per_revolution, step_time):
        self._motor = motor
        self._backlash = backlash
        self._mm_per_revolution = mm_per_revolution
        self._steps_per_revolution = steps_per_revolution
        self._step_time = step_time
        self._last_sign = 0

    @property
    def step_time(self):
        return self._step_time

    @property
    def motor(self):
        return self._motor

    def steps_needed_to_move_by(self, amount_mm):
        return int(
            self._steps_per_revolution *
            amount_mm /
            self._mm_per_revolution
        )

    def initialize(self):
        # Situation ---|???????| - partially unknown tool position
        for unused_i in range(int(self.steps_per_mm(self._backlash / 2.0))):
            self._motor.step_left(self._step_time)

        # Situation |   ????|
        for unused_i in range(int(self.steps_per_mm(self._backlash))):
            self._motor.step_right(self._step_time)

        # Situation ------|?       |
        for unused_i in range(int(self.steps_per_mm(self._backlash / 2.0))):
            self._motor.step_left(self._step_time)

        # Situation ---|   T   | - tool position fully known - TODO update docs

    def compensate_for_backlash(self, amount):
        if amount > 0:
            sign = 1
        elif amount == 0:
            sign = 0
        else:  # amount < 0
            sign = -1

        if sign == 1:
            if self._last_sign == 0:
                for i in range(int(self.steps_per_mm(self._backlash / 2.0))):
                    self._motor.step_left(self._step_time)
            elif self._last_sign == -1:
                for i in range(int(self.steps_per_mm(self._backlash))):
                    self._motor.step_left(self._step_time)

            self._last_sign = sign
        elif sign == -1:
            if self._last_sign == 0:
                for i in range(int(self.steps_per_mm(self._backlash / 2.0))):
                    self._motor.step_right(self._step_time)
            elif self._last_sign == 1:
                for i in range(int(self.steps_per_mm(self._backlash))):
                    self._motor.step_right(self._step_time)
            self._last_sign = sign

    def steps_per_mm(self, mm):
        return self._steps_per_revolution * mm / self._mm_per_revolution


class StepperMotorControlMachine:
    def __init__(self, x_axis, y_axis, z_axis, default_feed_rate, rapid_move_feed_rate):
        self._x_axis = x_axis
        self._y_axis = y_axis
        self._z_axis = z_axis
        self._initialized = False
        self._default_feed_rate = default_feed_rate
        self._rapid_move_feed_rate = rapid_move_feed_rate

    def initialize(self):
        self._initialized = True
        self._x_axis.initialize()
        self._y_axis.initialize()
        self._z_axis.initialize()

    def move_by(self, x, y, z, feed_rate):
        if not self._initialized:
            raise MachineUseException("Uninitialized machine")

        self._compensate_for_backlash(x, y, z)

        x_steps = self._x_axis.steps_needed_to_move_by(x)
        y_steps = self._y_axis.steps_needed_to_move_by(y)
        z_steps = self._z_axis.steps_needed_to_move_by(z)

        if x_steps == 0 and y_steps == 0 and z_steps == 0:
            return

        length = math.sqrt(
            (x_steps / self._x_axis.steps_per_mm(1)) ** 2 +
            (y_steps / self._y_axis.steps_per_mm(1)) ** 2 +
            (z_steps / self._z_axis.steps_per_mm(1)) ** 2)  # move length in mm
        total_time = 60.0 * length / feed_rate  # speed is in mm/min

        if x_steps < 0:
            x_steps = abs(x_steps)
            self._x_axis.motor.signal_go_right()
        else:
            self._x_axis.motor.signal_go_left()

        if y_steps < 0:
            y_steps = abs(y_steps)
            self._y_axis.motor.signal_go_right()
        else:
            self._y_axis.motor.signal_go_left()

        if z_steps < 0:
            z_steps = abs(z_steps)
            self._z_axis.motor.signal_go_right()
        else:
            self._z_axis.motor.signal_go_left()

        assert self._x_axis.step_time == self._y_axis.step_time
        assert self._y_axis.step_time == self._z_axis.step_time

        steps_sequence = create_xyz_steps_sequence(
            x_steps,
            y_steps,
            z_steps,
        )
        step_time = total_time / len(steps_sequence)

        current_time = 0
        for event_time, axis in steps_sequence:
            motor = None
            if axis == 'X':
                 motor = self._x_axis.motor
            elif axis == 'Y':
                 motor = self._y_axis.motor
            elif axis == 'Z':
                 motor = self._z_axis.motor
            else:
                assert(False)

            motor.step(step_time)

    @property
    def default_feed_rate(self):
        return self._default_feed_rate

    @property
    def rapid_move_feed_rate(self):
        return self._rapid_move_feed_rate

    def _compensate_for_backlash(self, x, y, z):
        self._x_axis.compensate_for_backlash(x)
        self._y_axis.compensate_for_backlash(y)
        self._z_axis.compensate_for_backlash(z)
