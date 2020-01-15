from abc import (
    ABC,
    abstractmethod,
)

from utils.typing import Numeric


class BaseMachine(ABC):
    """
    Abstract machine, that receives move commands and executes them.

    It may be (and all three strategies are implemented as subclasses):

    - a simulated machine, that just collects the moves and can render them as a SVG file
    - an Arduino connected via serial port that interprets the moves
    - Raspbbery PI GPIO pins where stepper motor drivers are connected
    """
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the connection with the machine.
        """
        raise NotImplementedError

    @abstractmethod
    def flush(self) -> None:
        """
        If any commands have been cached, flush the cache.
        """
        raise NotImplementedError

    @abstractmethod
    def move_by(self, x: Numeric, y: Numeric, z: Numeric, feed_rate: Numeric) -> None:
        """
        Move the tool by a vector with given feed rate (mm/s).
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def default_feed_rate(self) -> Numeric:
        """
        The default feed rate when milling.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def rapid_move_feed_rate(self) -> Numeric:
        """
        The default feed rate when moving the tool, but not milling.
        """
        raise NotImplementedError
