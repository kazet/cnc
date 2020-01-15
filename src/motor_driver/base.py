from abc import ABC
import time

from typeguard import typechecked

from utils.typing import Numeric


class BaseMotorDriver(ABC):
    """
    An abstract class describing a stepper motor driver.
    """
    def signal_go_left(self) -> None:
        """
        Signal, that the direction of next moves would be "left".
        """
        raise NotImplementedError

    def signal_go_right(self) -> None:
        """
        Signal, that the direction of next moves would be "right".
        """
        raise NotImplementedError

    def signal_pul_up(self) -> None:
        """
        One "up" pulse, that together with a "down" pulse will constitute a move one step
        in given direction, whatever it is.
        """
        raise NotImplementedError

    def signal_pul_down(self) -> None:
        """
        One "down" pulse, that together with an "up" pulse will constitute a move one step
        in given direction, whatever it is.
        """
        raise NotImplementedError

    @typechecked
    def step_left(self, step_time: Numeric) -> None:
        """
        One "left" step.
        """
        self.signal_go_left()
        self.step(step_time)

    @typechecked
    def step_right(self, step_time: Numeric) -> None:
        """
        One "right" step.
        """
        self.signal_go_right()
        self.step(step_time)

    @typechecked
    def step(self, step_time: Numeric) -> None:
        """
        One step in given direction.
        """
        self.signal_pul_up()
        time.sleep(step_time / 2.0)
        self.signal_pul_down()
        time.sleep(step_time / 2.0)
