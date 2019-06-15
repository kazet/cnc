import math

import pygcode
import pygcode.gcodes

from tool_position import ThreeAxesToolPositionContainer
from utils.math_utils import euclidean_distance


class Mode():
    ABSOLUTE = 0
    INCREMENTAL = 1


class Plane():
    XY = 0
    ZX = 1
    YZ = 2


class InvalidGCodeException(Exception):
    def __init__(self, message):
        self.message = message


class GCodeInterpreter():
    def __init__(self, machine):
        self._machine = machine
        self._tool_positions = ThreeAxesToolPositionContainer()
        self._zero_tool_planes_feed()

    def run_gcode_string(self, input_text):
        for input_line in input_text.split('\n'):
            line = pygcode.Line(input_line)
            for gcode in line.block.gcodes:
                self.run_gcode_command(gcode)
                self._machine.flush()

    def run_gcode_command(self, gcode):
        if isinstance(gcode, pygcode.gcodes.GCodeIncrementalDistanceMode):
            self._mode = Mode.INCREMENTAL
        elif isinstance(gcode, pygcode.gcodes.GCodeAbsoluteDistanceMode):
            self._mode = Mode.ABSOLUTE
        elif isinstance(gcode, pygcode.gcodes.GCodeSelectXYPlane):
            self._plane = Plane.XY
        elif isinstance(gcode, pygcode.gcodes.GCodeLineNumber):
            pass
        elif isinstance(gcode, pygcode.gcodes.GCodeUseMillimeters):
            pass
        elif isinstance(gcode, pygcode.gcodes.GCodeArcMoveCW) or isinstance(gcode, pygcode.gcodes.GCodeArcMoveCCW):
            x = self._coordinates_to_incremental(
                'X',
                gcode.get_param_dict().get('X', 0),
                self._mode,
            )

            y = self._coordinates_to_incremental(
                'Y',
                gcode.get_param_dict().get('Y', 0),
                self._mode,
            )

            z = self._coordinates_to_incremental(
                'Z',
                gcode.get_param_dict().get('Z', 0),
                self._mode,
            )

            if isinstance(gcode, pygcode.gcodes.GCodeArcMoveCW):
                angular_direction = -1
            elif isinstance(gcode, pygcode.gcodes.GCodeArcMoveCCW):
                angular_direction = 1
            else:
                assert(False)

            self._arc(angular_direction, x, y, 0, gcode.get_param_dict())

        elif isinstance(gcode, pygcode.gcodes.GCodeRapidMove) or isinstance(gcode, pygcode.gcodes.GCodeLinearMove):
            if len(set(gcode.get_param_dict().keys()) - set(['X', 'Y', 'Z'])) > 0:
                raise InvalidGCodeException("Unknown axes in %s" % repr(gcode.get_param_dict()))

            if 'X' in gcode.get_param_dict():
                x = self._coordinates_to_incremental(
                    'X',
                    gcode.get_param_dict()['X'],
                    self._mode,
                )
            else:
                x = 0

            if 'Y' in gcode.get_param_dict():
                y = self._coordinates_to_incremental(
                    'Y',
                    gcode.get_param_dict()['Y'],
                    self._mode,
                )
            else:
                y = 0

            if 'Z' in gcode.get_param_dict():
                z = self._coordinates_to_incremental(
                    'Z',
                    gcode.get_param_dict()['Z'],
                    self._mode,
                )
            else:
                z = 0

            if isinstance(gcode, pygcode.gcodes.GCodeRapidMove):
                self._move_by_and_update_tool_position(
                    x,
                    y,
                    z,
                    self._machine.rapid_move_feed_rate,
                )
            elif isinstance(gcode, pygcode.gcodes.GCodeLinearMove):
                self._move_by_and_update_tool_position(
                    x,
                    y,
                    z,
                    self._feed_rate,
                )
            else:
                assert(False)

        elif isinstance(gcode, pygcode.gcodes.GCodeFeedRate):
            self._feed_rate = gcode.word.value
        else:
            raise InvalidGCodeException("Unknown GCode: %s" % gcode.__class__)

    def _arc(self, angular_direction, finish_x, finish_y, finish_z, parameters):
        RADIUS_EPSILON = 10**(-2)
        NUM_ANGULAR_STEPS = 60

        start_tool_position_x = self._tool_positions.x.tool_position
        start_tool_position_y = self._tool_positions.y.tool_position
        start_tool_position_z = self._tool_positions.z.tool_position

        if angular_direction not in [-1, 1]:
            raise Exception("Unknown angular direction: %s" % repr(angular_direction))

        if self._plane is None:
            raise Exception("Unable to draw an arc - no plane seleted")
        elif self._plane != Plane.XY:
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

        radius = euclidean_distance((0, 0, 0), (center_x, center_y, 0))
        radius2 = euclidean_distance((finish_x, finish_y, 0), (center_x, center_y, 0))

        if abs(radius - radius2) > RADIUS_EPSILON:
            raise Exception("Radia mismatch: %0.6f vs %.06f" % (
                radius,
                radius2,
            ))

        if abs(radius) <= RADIUS_EPSILON:
            raise Exception("Null radius")

        angle_step = angular_direction * (2 * math.pi) / NUM_ANGULAR_STEPS
        one_step_distance = euclidean_distance(
            (0, radius, 0),
            (radius * math.sin(angle_step), radius * math.cos(angle_step), 0))

        start_angle = math.atan2(0 - center_y, 0 - center_x)
        angle = start_angle

        while True:
            current_x = center_x + radius * math.cos(angle)
            current_y = center_y + radius * math.sin(angle)

            if euclidean_distance((current_x, current_y, 0), (finish_x, finish_y, 0)) < one_step_distance:
                break

            self._move_to_absolute(
                start_tool_position_x + current_x,
                start_tool_position_y + current_y,
                start_tool_position_z)
            angle += angle_step

        self._move_to_absolute(
            start_tool_position_x + finish_x,
            start_tool_position_y + finish_y,
            start_tool_position_z)

    def _move_to_absolute(self, x, y, z):
        self._move_by_and_update_tool_position(
            x - self._tool_positions.x.tool_position,
            y - self._tool_positions.y.tool_position,
            z - self._tool_positions.z.tool_position,
            self._feed_rate,
        )

    def _move_by_and_update_tool_position(self, x, y, z, feed_rate):
        self._machine.move_by(x, y, z, feed_rate)
        self._tool_positions.x.add(x)
        self._tool_positions.y.add(y)
        self._tool_positions.z.add(z)

    def _get_axis_position(self, axis):
        return {
            'X': self._tool_positions.x.tool_position,
            'Y': self._tool_positions.y.tool_position,
            'Z': self._tool_positions.z.tool_position,
        }[axis]

    def _coordinates_to_incremental(self, axis, position, mode):
        if mode == Mode.ABSOLUTE:
            return position - self._get_axis_position(axis)
        elif mode == Mode.INCREMENTAL:
            return position
        else:
            assert(False)

    def _zero_tool_planes_feed(self):
        """
        Resets the GCodeInterpreter configuration. Thet means, that:

        - the tool positions will be reset to zero
        - the arc plane will be reset to the XY plane
        - the mode (absolute vs relative) will be reset to absolute
        - the feed rate will be reset to the default
        """

        self._tool_positions.zero_tool_positions()
        self._plane = Plane.XY
        self._mode = Mode.ABSOLUTE
        self._feed_rate = self._machine.default_feed_rate
