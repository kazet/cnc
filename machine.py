import pygcode.gcodes

class MachineMode():
    ABSOLUTE = 0
    INCREMENTAL = 1


class MachineUseException(Exception):
    def __init__(self, message):
        self.message = message



class MachineAxis():
    def __init__(self, motor, slack, mm_per_revolution, steps_per_revolution, step_time):
        self._motor = motor
        self._tool_position = None
        self._positioner_position = None
        self._slack = slack
        self._mm_per_revolution = mm_per_revolution
        self._steps_per_revolution = steps_per_revolution
        self._step_time = step_time

    @property
    def step_time(self):
        return self._step_time

    @property
    def motor(self):
        return self._motor

    def initialize(self):
        # Situation ---|???????| - partially unknown tool position
        for unused_i in range(int(self._steps_for_mm(self._slack / 2.0))):
            self._motor.step_left(self._step_time)

        # Situation |   ????|
        for unused_i in range(int(self._steps_for_mm(self._slack))):
            self._motor.step_right(self._step_time)

        # Situation ------|?       |
        for unused_i in range(int(self._steps_for_mm(self._slack / 2.0))):
            self._motor.step_left(self._step_time)

        # Situation ---|   T   |
        self._tool_position = 0
        self._positioner_position = -self._slack / 2.0

    def steps_needed_to_move_to(self, new_tool_position, mode):
        if mode == MachineMode.ABSOLUTE:
            return (
                self._steps_per_revolution *
                (new_tool_position - self._tool_position) /
                self._mm_per_revolution
            )
        elif mode == MachineMode.INCREMENTAL:
            return (
                self._steps_per_revolution *
                new_tool_position /
                self._mm_per_revolution
            )
        else:
            assert(False)

    def compensate_for_slack(self, new_tool_position, mode):
        if mode == MachineMode.ABSOLUTE:
            if new_tool_position > self._tool_position:
                sign = 1
            elif new_tool_position == self._tool_position:
                sign = 0
            else:  # new_tool_position < self._tool_position
                sign = -1
        elif mode == MachineMode.INCREMENTAL:
            if new_tool_position > 0:
                sign = 1
            elif new_tool_position == 0:
                sign = 0
            else:  # new_tool_position < 0
                sign = -1

        pass # TODO 

    def _steps_for_mm(self, mm):
        return self._steps_per_revolution * mm / self._mm_per_revolution


class Machine():
    def __init__(self, x_axis, y_axis):
        self._mode = MachineMode.ABSOLUTE
        self._x_axis = x_axis
        self._y_axis = y_axis

        self._initialized = False

    def _coordinated_move(self, x_steps, y_steps):
        if x_steps < 0:
            x_steps = abs(x_steps)
            x_stepper = self._x_axis.motor.step_right
        else:
            x_stepper = self._x_axis.motor.step_left

        if y_steps < 0:
            y_steps = abs(y_steps)
            y_stepper = self._y_axis.motor.step_right
        else:
            y_stepper = self._y_axis.motor.step_left

        x_steps_done = 0
        y_steps_done = 0

        print(x_steps, y_steps)
        while x_steps_done < x_steps or y_steps_done < y_steps:
            if y_steps > 0:
                if y_steps_done > 0:
                    if (x_steps_done / y_steps_done > x_steps / y_steps):
                        y_stepper(self._y_axis.step_time)
                        y_steps_done += 1
                    else:
                        x_stepper(self._x_axis.step_time)
                        x_steps_done += 1
                else:
                    y_stepper(self._y_axis.step_time)
                    y_steps_done += 1
            else:
                x_stepper(self._x_axis.step_time)
                x_steps_done += 1

    def feed(self, gcode):
        if not self._initialized:
            raise MachineUseException("Uninitialized machine")

        if isinstance(gcode, pygcode.gcodes.GCodeIncrementalDistanceMode):
            self._mode = MachineMode.INCREMENTAL
        elif isinstance(gcode, pygcode.gcodes.GCodeRapidMove):
            if len(set(gcode.get_param_dict().keys()) - set(['X', 'Y', 'Z'])) > 0:
                raise MachineUseException("Unknown axes in %s" % repr(gcode.get_param_dict()))

            self._x_axis.compensate_for_slack(
                gcode.get_param_dict()['X'],
                self._mode
            )
            self._y_axis.compensate_for_slack(
                gcode.get_param_dict()['Y'],
                self._mode
            )

            x_steps = self._x_axis.steps_needed_to_move_to(
                gcode.get_param_dict()['X'],
                self._mode
            )
            y_steps = self._x_axis.steps_needed_to_move_to(
                gcode.get_param_dict()['Y'],
                self._mode
            )
            self._coordinated_move(x_steps, y_steps)
        else:
            raise MachineUseException("Unknown GCode: %s" % gcode.__class__)

    def initialize(self):
        self._x_axis.initialize()
        self._y_axis.initialize()
        self._initialized = True
