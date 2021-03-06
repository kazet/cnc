import math

from machine.base import BaseMachine
from motor_driver.base import BaseMotorDriver
from utils.steps_sequence import create_xyz_steps_sequence
from utils.typing import Numeric
from exceptions import MachineCommunicationException
from typeguard import typechecked


class MachineAxis:
    """
    One axis, where one stepper motor, that we control, is connected.
    """

    @typechecked
    def __init__(
            self,
            motor: BaseMotorDriver,
            backlash: Numeric,
            mm_per_revolution: Numeric,
            steps_per_revolution: Numeric,
            step_time: Numeric) -> None:
        self._motor = motor
        self._backlash = backlash
        self._mm_per_revolution = mm_per_revolution
        self._steps_per_revolution = steps_per_revolution
        self._step_time = step_time
        self._last_sign = 0

    @property
    @typechecked
    def step_time(self) -> Numeric:
        return self._step_time

    @property
    @typechecked
    def motor(self) -> BaseMotorDriver:
        return self._motor

    @typechecked
    def steps_needed_to_move_by(self, amount_mm) -> Numeric:
        return int(
            self._steps_per_revolution *
            amount_mm /
            self._mm_per_revolution
        )

    @typechecked
    def initialize(self) -> None:
        # The existence of a backlash means, that the tool can move self._backlash
        # milimeters to the left or to the right when force is applied.
        #
        # Therefore, the starting position may be anywhere from -self._backlash/2 to
        # +self._backlash/2 from 'zero'.
        #
        # We make the following movements to make sure where the tool is:
        #
        # Initial situation:       ---|TTTTTTT|     - partially unknown tool position
        # Move to the left:        |   TTTT|        - the tool may be anywhere from
        #                                             -self._backlash to 0, because
        #                                             if it was more to the right, it would
        #                                             have moved
        # Move to the right:       ------|T       | - we now know the tool position
        # Second move to the left: ---|   T   |
        #
        # Any later movements will need to take in the account, that when moving the tool,
        # the first self._backlash/2 of the movement will not do anything. Only later
        # will the tool start moving.

        for unused_i in range(int(self.steps_per_mm(self._backlash / 2.0))):
            self._motor.step_left(self._step_time)

        for unused_i in range(int(self.steps_per_mm(self._backlash))):
            self._motor.step_right(self._step_time)

        for unused_i in range(int(self.steps_per_mm(self._backlash / 2.0))):
            self._motor.step_left(self._step_time)

    @typechecked
    def compensate_for_backlash(self, amount: Numeric) -> None:
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

    @typechecked
    def steps_per_mm(self, mm: Numeric) -> Numeric:
        return self._steps_per_revolution * mm / self._mm_per_revolution


class StepperMotorControlMachine(BaseMachine):
    """
    An implementation of a BaseMachine that has 3 axes controlled by separate BaseMotorDrivers.
    """
    @typechecked
    def __init__(
            self,
            x_axis: MachineAxis,
            y_axis: MachineAxis,
            z_axis: MachineAxis,
            default_feed_rate: Numeric,
            rapid_move_feed_rate: Numeric):
        self._x_axis = x_axis
        self._y_axis = y_axis
        self._z_axis = z_axis
        self._initialized = False
        self._default_feed_rate = default_feed_rate
        self._rapid_move_feed_rate = rapid_move_feed_rate

    @typechecked
    def initialize(self) -> None:
        self._initialized = True
        self._x_axis.initialize()
        self._y_axis.initialize()
        self._z_axis.initialize()

    @typechecked
    def flush(self) -> None:
        pass

    @typechecked
    def move_by(self, x: Numeric, y: Numeric, z: Numeric, feed_rate: Numeric) -> None:
        if not self._initialized:
            raise MachineCommunicationException("Uninitialized machine")

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
    @typechecked
    def default_feed_rate(self) -> Numeric:
        return self._default_feed_rate

    @property
    @typechecked
    def rapid_move_feed_rate(self) -> Numeric:
        return self._rapid_move_feed_rate

    def _compensate_for_backlash(self, x: Numeric, y: Numeric, z: Numeric) -> None:
        self._x_axis.compensate_for_backlash(x)
        self._y_axis.compensate_for_backlash(y)
        self._z_axis.compensate_for_backlash(z)
