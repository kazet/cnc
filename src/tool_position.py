class AxisToolPosition():
    def __init__(self):
        self._tool_position = 0

    def zero_tool_position(self):
        """
        Set the tool positions to zero (without doing anything to the
        milling machine) - i. e. pretend, that the point zero is where the
        current tool location is.
        """
        self._tool_position = 0

    def add(self, how_much):
        """
        Adds a given value to tool position.

        Arguments:
            how_much: how much to add
        """
        self._tool_position += how_much

    @property
    def tool_position(self):
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
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z
