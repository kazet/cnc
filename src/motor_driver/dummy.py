from typeguard import typechecked

from utils.typing import Numeric
from motor_driver.base import BaseMotorDriver


class DummyMotorDriver(BaseMotorDriver):
    """
    A dummy implementation of BaseMotorDriver that raises NotImplementedError on any command.
    """
    def __init__(self, *unused_args, **unused_kwargs):
        pass

    @typechecked
    def signal_go_left(self) -> None:
        """
        Please refer to the docstring in the base class.
        """
        self._raise()

    @typechecked
    def signal_go_right(self) -> None:
        """
        Please refer to the docstring in the base class.
        """
        self._raise()

    @typechecked
    def signal_pul_up(self) -> None:
        """
        Please refer to the docstring in the base class.
        """
        self._raise()

    @typechecked
    def signal_pul_down(self) -> None:
        """
        Please refer to the docstring in the base class.
        """
        self._raise()

    @typechecked
    def step_left(self, step_time: Numeric) -> None:
        """
        Please refer to the docstring in the base class.
        """
        self._raise()

    @typechecked
    def step_right(self, step_time: Numeric) -> None:
        """
        Please refer to the docstring in the base class.
        """
        self._raise()

    @typechecked
    def step(self, step_time: Numeric) -> None:
        """
        Please refer to the docstring in the base class.
        """
        self._raise()

    def _raise(self):
        raise NotImplementedError("No actual milling machine connected")
