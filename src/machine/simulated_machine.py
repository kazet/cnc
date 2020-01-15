import typing

from typeguard import typechecked

from machine.base import BaseMachine
from utils.typing import Numeric


class SimulatedMachine(BaseMachine):
    """
    An implementation of a Machine that just simulates the moves
    so that they may be collected, and, for example, rendered as SVG.
    """

    def __init__(self):
        self._simulated_moves = [(0, 0, 0, False)]
        self._default_feed_rate = 1
        self._rapid_move_feed_rate = 10
        self._tool_position_x = 0
        self._tool_position_y = 0
        self._tool_position_z = 0

    @typechecked
    def initialize(self) -> None:
        """
        Please refer to the docstring in the base class.
        """
        pass

    @typechecked
    def flush(self) -> None:
        """
        Please refer to the docstring in the base class.
        """
        pass

    @typechecked
    def move_by(self, x: Numeric, y: Numeric, z: Numeric, feed_rate: Numeric) -> None:
        """
        Please refer to the docstring in the base class.
        """
        if feed_rate == self._default_feed_rate:
            is_rapid = False
        elif feed_rate == self._rapid_move_feed_rate:
            is_rapid = True
        else:
            is_rapid = False

        # We don't use the tool position from GCodeInterpreter, because we want to be
        # more realistic: the machine has its own tool position, and the interpreter role
        # is just to model it.
        self._tool_position_x += x
        self._tool_position_y += y
        self._tool_position_z += z

        self._simulated_moves.append((
            self._tool_position_x,
            self._tool_position_y,
            self._tool_position_z,
            is_rapid
        ))

    @property
    @typechecked
    def simulated_moves(self) -> typing.List[typing.Tuple[Numeric, Numeric, Numeric, bool]]:
        """
        Returns the collected simulated moves.

        :return: a list of tuples (x, y, z, if the move was a rapid move (i.e. not milling)).
        """
        return self._simulated_moves

    @property
    @typechecked
    def default_feed_rate(self) -> Numeric:
        """
        Please refer to the docstring in the base class.
        """
        return self._default_feed_rate

    @property
    @typechecked
    def rapid_move_feed_rate(self) -> Numeric:
        """
        Please refer to the docstring in the base class.
        """
        return self._rapid_move_feed_rate
