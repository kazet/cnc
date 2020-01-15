import typing

import RPi.GPIO
from typeguard import typechecked

from src.motor_driver.base import BaseMotorDriver


class RaspberryPiGPIOMotorDriver(BaseMotorDriver):
    """
    An implementation of BaseMotorDriver that uses Raspberry Pi GPIO pins with a stepper motor
    controller connected to drive a stepper motor.
    """
    @typechecked
    def __init__(self, motor_pins: typing.Dict[str, int], is_inverse: bool = False) -> None:
        """
        :param motor_pins:
            a dict with two keys:
                DIR - where the Direction pin is connected,
                PUL - where the Pulse pin is connected.
        :param is_inverse: whether the direction should be inverted.
        """
        self._is_inverse = is_inverse
        self._motor_pins = motor_pins

        self._configure_gpio()

    @typechecked
    def signal_go_left(self) -> None:
        """
        Please refer to the docstring in the base class.
        """
        self._output(
            self._motor_pins['DIR'],
            0 if self._is_inverse else 1
        )

    def signal_go_right(self) -> None:
        """
        Please refer to the docstring in the base class.
        """
        self._output(
            self._motor_pins['DIR'],
            1 if self._is_inverse else 0
        )

    @typechecked
    def signal_pul_up(self) -> None:
        """
        Please refer to the docstring in the base class.
        """
        self._output(
            self._motor_pins['PUL'],
            1
        )

    @typechecked
    def signal_pul_down(self) -> None:
        """
        Please refer to the docstring in the base class.
        """
        self._output(
            self._motor_pins['PUL'],
            0
        )

    @typechecked
    def _configure_gpio(self) -> None:
        RPi.GPIO.setmode(RPi.GPIO.BOARD)

        for motor_pin in self._motor_pins.values():
            RPi.GPIO.setup(motor_pin, RPi.GPIO.OUT)

    @typechecked
    def _output(self, pin: int, value: int) -> None:
        RPi.GPIO.output(pin, value)
