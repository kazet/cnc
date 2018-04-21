import time

import pygcode.gcodes

from steps_sequence import create_xyz_steps_sequence


class MachineMode():
    ABSOLUTE = 0
    INCREMENTAL = 1


class MachineUseException(Exception):
    def __init__(self, message):
        self.message = message


class BaseMachineAxis():
    def __init__(self, mm_per_revolution, steps_per_revolution):
        self._mm_per_revolution = mm_per_revolution
        self._steps_per_revolution = steps_per_revolution

    @property
    def tool_position(self):
        return self._tool_position

    def coordinates_to_incremental(self, pos, mode):
        if mode == MachineMode.ABSOLUTE:
            return pos - self._tool_position
        elif mode == MachineMode.INCREMENTAL:
            return pos
        else:
            assert(False)

    def update_tool_position(self, steps):
        self._tool_position += steps / self.steps_per_mm

    def steps_needed_to_move_by(self, amount_mm):
        return int(
            self._steps_per_revolution *
            amount_mm /
            self._mm_per_revolution
        )


class SimulatedMachineAxis(BaseMachineAxis):
    def __init__(self, mm_per_revolution, steps_per_revolution):
        super().__init__(mm_per_revolution, steps_per_revolution)
        self._tool_position = 0

    @property
    def steps_per_mm(self):
        return self._steps_per_revolution / self._mm_per_revolution

    def initialize(self):
        pass

    def is_simulated(self):
        return True

    def compensate_for_backlash(self, new_tool_position):
        pass


class MachineAxis(BaseMachineAxis):
    def __init__(self, motor, backlash, mm_per_revolution, steps_per_revolution, step_time):
        super().__init__(mm_per_revolution, steps_per_revolution)
        self._motor = motor
        self._tool_position = None
        self._positioner_position = None
        self._backlash = backlash
        self._step_time = step_time

    @property
    def step_time(self):
        return self._step_time

    @property
    def motor(self):
        return self._motor

    def is_simulated(self):
        return False

    def initialize(self):
        # Situation ---|???????| - partially unknown tool position
        for unused_i in range(int(self._steps_for_mm(self._backlash / 2.0))):
            self._motor.step_left(self._step_time)

        # Situation |   ????|
        for unused_i in range(int(self._steps_for_mm(self._backlash))):
            self._motor.step_right(self._step_time)

        # Situation ------|?       |
        for unused_i in range(int(self._steps_for_mm(self._backlash / 2.0))):
            self._motor.step_left(self._step_time)

        # Situation ---|   T   |
        self._tool_position = 0
        self._positioner_position = -self._backlash / 2.0

    def compensate_for_backlash(self, amount):
        if amount > 0:
            sign = 1
        elif amount == 0:
            sign = 0
        else:  # amount < 0
            sign = -1

        pass # TODO

    def _steps_for_mm(self, mm):
        return self._steps_per_revolution * mm / self._mm_per_revolution


class Machine():
    def __init__(self, x_axis, y_axis, simulated=False):
        self._mode = MachineMode.ABSOLUTE
        self._x_axis = x_axis
        self._y_axis = y_axis
        self._simulated = simulated
        self._simulated_moves = [(0, 0)]

        if simulated:
            self._initialized = True
        else:
            self._initialized = False

    @property
    def x_axis(self):
        return self._x_axis

    @property
    def y_axis(self):
        return self._y_axis

    @property
    def simulated_moves(self):
        assert self._simulated
        assert self._x_axis.is_simulated()
        assert self._y_axis.is_simulated()
        return self._simulated_moves

    def move_to(self, x, y):
        self._x_axis.compensate_for_backlash(x)
        self._y_axis.compensate_for_backlash(y)

        x_steps = self._x_axis.steps_needed_to_move_by(x)
        y_steps = self._y_axis.steps_needed_to_move_by(y)
        self._coordinated_move(x_steps, y_steps)

    def feed(self, gcode):
        if not self._initialized:
            raise MachineUseException("Uninitialized machine")

        if isinstance(gcode, pygcode.gcodes.GCodeIncrementalDistanceMode):
            self._mode = MachineMode.INCREMENTAL
        elif isinstance(gcode, pygcode.gcodes.GCodeAbsoluteDistanceMode):
            self._mode = MachineMode.ABSOLUTE
        elif isinstance(gcode, pygcode.gcodes.GCodeRapidMove):
            if len(set(gcode.get_param_dict().keys()) - set(['X', 'Y', 'Z'])) > 0:
                raise MachineUseException("Unknown axes in %s" % repr(gcode.get_param_dict()))

            x = self._x_axis.coordinates_to_incremental(
                gcode.get_param_dict().get('X', 0),
                self._mode,
            )

            y = self._y_axis.coordinates_to_incremental(
                gcode.get_param_dict().get('Y', 0),
                self._mode,
            )

            self.move_to(x, y)
        else:
            raise MachineUseException("Unknown GCode: %s" % gcode.__class__)

    def initialize(self):
        self._x_axis.initialize()
        self._y_axis.initialize()
        self._initialized = True

    def _coordinated_move(self, x_steps, y_steps):
        self._x_axis.update_tool_position(x_steps)
        self._y_axis.update_tool_position(y_steps)

        if self._simulated:
            assert self._x_axis.is_simulated()
            assert self._y_axis.is_simulated()
            self._simulated_moves.append((self._x_axis.tool_position, self._y_axis.tool_position))
            return
        else:
            assert not self._x_axis.is_simulated()
            assert not self._y_axis.is_simulated()

            TOO_SMALL_TIME_TO_SLEEP = 10 ** (-6)

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

            assert self._x_axis.step_time == self._y_axis.step_time

            steps_sequence = create_xyz_steps_sequence(
                self._x_axis.step_time,
                self._x_axis.step_time * 10,
                x_steps,
                y_steps,
                0
            )

            current_time = 0
            for event_time, axis, pulse_type in steps_sequence:
                motor = None
                if axis == 'X':
                     motor = self._x_axis.motor
                elif axis == 'Y':
                     motor = self._y_axis.motor
                else:
                    assert(False)

                if abs(event_time - current_time) >= TOO_SMALL_TIME_TO_SLEEP:
                    time.sleep(event_time - current_time)
                    current_time = event_time

                if pulse_type == 'UP':
                    motor.signal_pul_up()
                elif pulse_type == 'DOWN':
                    motor.signal_pul_down()
                else:
                    assert(False)
