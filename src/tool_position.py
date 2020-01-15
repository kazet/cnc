from typeguard import typechecked

from utils.typing import Numeric


class AxisToolPosition():
    """
    A class to manage tool position in one axis.
    """
    def __init__(self):
        self._tool_position = 0

    def zero_tool_position(self):
        """
        Set the tool positions to zero (without doing anything to the
        milling machine) - i. e. pretend, that the point zero is where the
        current tool location is.
        """
        self._tool_position = 0

    @typechecked
    def add(self, how_much: Numeric) -> None:
        """
        Adds a given value to tool position.

        Arguments:
            how_much: how much to add
        """
        self._tool_position += how_much

    @property
    def tool_position(self):
        """
        Return the current tool position.
        """
        return self._tool_position


class ThreeAxesToolPositionContainer():
    """
    Stores a three-dimensional (X, Y and Z) milling machine tool position,
    relative to some starting point.

    Attributes:
        x: x axis tool position (an AxisToolPosition)
        y: y axis tool position (an AxisToolPosition)
        z: z axis tool position (an AxisToolPosition)
    """
    def __init__(self):
        self._x = AxisToolPosition()
        self._y = AxisToolPosition()
        self._z = AxisToolPosition()

    def zero_tool_positions(self):
        """
        Set all tool positions to zero (without doing anything to the
        milling machine) - i. e. pretend, that the point zero is where the
        current tool location is.
        """
        self._x.zero_tool_position()
        self._y.zero_tool_position()
        self._z.zero_tool_position()

    @property
    def x(self):
        """
        Return the current tool position on X axis.
        """
        return self._x

    @property
    def y(self):
        """
        Return the current tool position on Y axis.
        """
        return self._y

    @property
    def z(self):
        """
        Return the current tool position on Z axis.
        """
        return self._z
