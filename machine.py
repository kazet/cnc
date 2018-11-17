import math
import time

import pygcode.gcodes

from steps_sequence import create_xyz_steps_sequence


class MachineMode():
    ABSOLUTE = 0
    INCREMENTAL = 1


class MachinePlane():
    XY = 0
    ZX = 1
    YZ = 2


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

    @property
    def steps_per_mm(self):
        return self._steps_per_revolution / self._mm_per_revolution

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

    def zero_tool_position(self):
        self._tool_position = 0

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
        self._last_sign = 0

    @property
    def step_time(self):
        return self._step_time

    @property
    def motor(self):
        return self._motor

    def is_simulated(self):
        return False

    def zero_tool_position(self):
        # TODO positioner
        self._tool_position = 0

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

        print("B", sign, self._last_sign, self._motor._axis)
        if sign == 1:
            if self._last_sign == 0:
                for i in range(int(self._steps_for_mm(self._backlash / 2.0))):
                    self._motor.step_left(self._step_time)
            elif self._last_sign == -1:
                for i in range(int(self._steps_for_mm(self._backlash))):
                    self._motor.step_left(self._step_time)

            self._last_sign = sign
        elif sign == -1:
            if self._last_sign == 0:
                for i in range(int(self._steps_for_mm(self._backlash / 2.0))):
                    self._motor.step_right(self._step_time)
            elif self._last_sign == 1:
                for i in range(int(self._steps_for_mm(self._backlash))):
                    self._motor.step_right(self._step_time)
            self._last_sign = sign

    def _steps_for_mm(self, mm):
        return self._steps_per_revolution * mm / self._mm_per_revolution


class Machine():
    DEFAULT_FEED_RATE = 1000

    def __init__(self, x_axis, y_axis, z_axis, simulated=False):
        self._plane = None
        self._mode = MachineMode.ABSOLUTE
        self._x_axis = x_axis
        self._y_axis = y_axis
        self._z_axis = z_axis
        self._feed_rate = Machine.DEFAULT_FEED_RATE
        self._simulated = simulated
        self._simulated_moves = [(0, 0, 0)]

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
    def z_axis(self):
        return self._z_axis

    @property
    def simulated_moves(self):
        assert self._simulated
        assert self._x_axis.is_simulated()
        assert self._y_axis.is_simulated()
        assert self._z_axis.is_simulated()
        return self._simulated_moves

    def zero_tool_positions(self):
        self._x_axis.zero_tool_position()
        self._y_axis.zero_tool_position()
        self._z_axis.zero_tool_position()

    def move_to(self, x, y, z):
        self.move_by(
            x - self._x_axis.tool_position,
            y - self._y_axis.tool_position,
            z - self._z_axis.tool_position,
        )

    def move_by(self, x, y, z):
        self._x_axis.compensate_for_backlash(x)
        self._y_axis.compensate_for_backlash(y)
        self._z_axis.compensate_for_backlash(z)

        x_steps = self._x_axis.steps_needed_to_move_by(x)
        y_steps = self._y_axis.steps_needed_to_move_by(y)
        z_steps = self._z_axis.steps_needed_to_move_by(z)
        self._coordinated_move_by(x_steps, y_steps, z_steps, self._feed_rate)

    def arc(self, angular_direction, finish_x, finish_y, finish_z, parameters):
        RADIUS_EPSILON = 10**(-2)
        NUM_ANGULAR_STEPS = 60

        start_tool_position_x = self._x_axis.tool_position
        start_tool_position_y = self._y_axis.tool_position
        start_tool_position_z = self._z_axis.tool_position

        if angular_direction not in [-1, 1]:
            raise Exception("Unknown angular direction: %s" % repr(angular_direction))

        if self._plane is None:
            raise Exception("Unable to draw an arc - no plane seleted")
        elif self._plane != MachinePlane.XY:
            raise NotImplementedError("Non-XY arcs are not supported")

        if 'I' and 'J' in parameters.keys():
            center_x = parameters['I']
            center_y = parameters['J']
        elif 'R' in parameters.keys():
            raise NotImplementedError()
        else:
            raise Exception("Expected either I and J or R in GCode parameters")

        if finish_z != 0:
            raise NotImplementedError("Helical moves are not supported")

        angle1 = math.atan2(0 - center_y, 0 - center_x)
        angle2 = math.atan2(finish_y - center_y, finish_x - center_x)

        radius = self._distance((0, 0, 0), (center_x, center_y, 0))
        radius2 = self._distance((finish_x, finish_y, 0), (center_x, center_y, 0))

        if abs(radius - radius2) > RADIUS_EPSILON:
            raise Exception("Radia mismatch: %0.6f vs %.06f" % (
                radius,
                radius2,
            ))

        angle_step = angular_direction * (2 * math.pi) / NUM_ANGULAR_STEPS
        one_step_distance = self._distance(
            (0, radius, 0),
            (radius * math.sin(angle_step), radius * math.cos(angle_step), 0))
        angle = angle1

        while True:
            current_x = center_x + radius * math.cos(angle)
            current_y = center_y + radius * math.sin(angle)

            if self._distance((current_x, current_y, 0), (finish_x, finish_y, 0)) < one_step_distance:
                break

            self.move_to(start_tool_position_x + current_x, start_tool_position_y + current_y, start_tool_position_z)
            angle += angle_step

        self.move_to(start_tool_position_x + finish_x, start_tool_position_y + finish_y, start_tool_position_z)

    def feed(self, gcode):
        if not self._initialized:
            raise MachineUseException("Uninitialized machine")

        if isinstance(gcode, pygcode.gcodes.GCodeIncrementalDistanceMode):
            self._mode = MachineMode.INCREMENTAL
        elif isinstance(gcode, pygcode.gcodes.GCodeAbsoluteDistanceMode):
            self._mode = MachineMode.ABSOLUTE
        elif isinstance(gcode, pygcode.gcodes.GCodeSelectXYPlane):
            self._plane = MachinePlane.XY
        elif isinstance(gcode, pygcode.gcodes.GCodeArcMoveCW) or isinstance(gcode, pygcode.gcodes.GCodeArcMoveCCW):
            x = self._x_axis.coordinates_to_incremental(
                gcode.get_param_dict().get('X', 0),
                self._mode,
            )

            y = self._y_axis.coordinates_to_incremental(
                gcode.get_param_dict().get('Y', 0),
                self._mode,
            )

            z = self._y_axis.coordinates_to_incremental(
                gcode.get_param_dict().get('Z', 0),
                self._mode,
            )


            if isinstance(gcode, pygcode.gcodes.GCodeArcMoveCW):
                angular_direction = -1
            elif isinstance(gcode, pygcode.gcodes.GCodeArcMoveCCW):
                angular_direction = 1
            else:
                assert(False)

            self.arc(angular_direction, x, y, 0, gcode.get_param_dict())

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

            z = self._y_axis.coordinates_to_incremental(
                gcode.get_param_dict().get('Z', 0),
                self._mode,
            )

            self.move_by(x, y, z)
        elif isinstance(gcode, pygcode.gcodes.GCodeFeedRate):
            self._feed_rate = gcode.word.value
        else:
            raise MachineUseException("Unknown GCode: %s" % gcode.__class__)

    def initialize(self):
        self._x_axis.initialize()
        self._y_axis.initialize()
        self._z_axis.initialize()
        self._initialized = True

    def _distance(self, point1, point2):
        x1, y1, z1 = point1
        x2, y2, z2 = point2

        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)

    def _coordinated_move_by(self, x_steps, y_steps, z_steps, speed):
        if x_steps == 0 and y_steps == 0 and z_steps == 0:
            return

        self._x_axis.update_tool_position(x_steps)
        self._y_axis.update_tool_position(y_steps)
        self._z_axis.update_tool_position(z_steps)

        if self._simulated:
            assert self._x_axis.is_simulated()
            assert self._y_axis.is_simulated()
            assert self._z_axis.is_simulated()
            self._simulated_moves.append((self._x_axis.tool_position, self._y_axis.tool_position, self._z_axis.tool_position))
            return
        else:
            assert not self._x_axis.is_simulated()
            assert not self._y_axis.is_simulated()
            assert not self._z_axis.is_simulated()

            length = math.sqrt(
                (x_steps / self._x_axis.steps_per_mm) ** 2 +
                (y_steps / self._y_axis.steps_per_mm) ** 2 +
                (z_steps / self._z_axis.steps_per_mm) ** 2)  # move length in mm
            total_time = 60.0 * length / speed  # speed is in mm/min
            step_time = total_time / max(abs(x_steps), abs(y_steps), abs(z_steps))

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

            if z_steps < 0:
                z_steps = abs(z_steps)
                self._z_axis.motor.signal_go_right()
            else:
                self._z_axis.motor.signal_go_left()

            assert self._x_axis.step_time == self._y_axis.step_time
            assert self._y_axis.step_time == self._z_axis.step_time

            steps_sequence = create_xyz_steps_sequence(
                step_time,
                step_time * 10,
                x_steps,
                y_steps,
                z_steps,
            )

            current_time = 0
            for event_time, axis, pulse_type in steps_sequence:
                motor = None
                if axis == 'X':
                     motor = self._x_axis.motor
                elif axis == 'Y':
                     motor = self._y_axis.motor
                elif axis == 'Z':
                     motor = self._z_axis.motor
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
