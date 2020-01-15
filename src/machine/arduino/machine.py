import logging
import glob
import serial
import struct
import time
import typing

from typeguard import typechecked

from machine.arduino import messages
from machine.base import BaseMachine
from exceptions import MachineCommunicationException
from utils.typing import Numeric


LOGGER = logging.getLogger('cnc')


class Arduino3AxisSerialMachineError(Exception):
    """
    There is a problem with communication with the attached Arduino.
    """
    pass


class Arduino3AxisSerialMachine(BaseMachine):
    """
    An implementation of a Machine that uses binary commands send via serial-port to an Arduino as a backend.

    The Arduino source code resides in ./src/machine/arduino/main/
    """
    @typechecked
    def __init__(
            self,
            steps_per_mm_x: Numeric,
            steps_per_mm_y: Numeric,
            steps_per_mm_z: Numeric,
            invert_x: bool,
            invert_y: bool,
            invert_z: bool,
            default_feed_rate: Numeric,
            rapid_move_feed_rate: Numeric,
            port_path_template: str = '/dev/ttyUSB*'):
        """
        :param steps_per_mm_x: how many stepper motor pulses are needed for one millimeter move on the X axis
        :param steps_per_mm_y: how many stepper motor pulses are needed for one millimeter move on the Y axis
        :param steps_per_mm_z: how many stepper motor pulses are needed for one millimeter move on the Z axis
        :param invert_x: if the X axis is inverted
        :param invert_y: if the Y axis is inverted
        :param invert_z: if the Z axis is inverted
        :param default_feed_rate: the default feed rate when milling
        :param rapid_move_feed_rate: the default feed rate when moving the tool
        """
        port = self._autodetect_port(port_path_template)
        if port:
            self._real_machine_connected = True
        else:
            LOGGER.error("Unable to detect serial port. To facilitate experiments, /dev/null will be used.")
            self._real_machine_connected = False

        self._ser = serial.Serial(port)
        self._initialized = False
        self._steps_per_mm_x = steps_per_mm_x
        self._steps_per_mm_y = steps_per_mm_y
        self._steps_per_mm_z = steps_per_mm_z
        self._invert_x = invert_x
        self._invert_y = invert_y
        self._invert_z = invert_z
        self._default_feed_rate = default_feed_rate
        self._rapid_move_feed_rate = rapid_move_feed_rate
        self._last_direction = {}

    def guard_that_a_real_machine_is_connected(self) -> None:
        if not self._real_machine_connected:
            raise Arduino3AxisSerialMachineError("No actual machine is connected")

    @typechecked
    def _autodetect_port(self, port_path_template: str) -> typing.Union[str, None]:
        detected_ports = glob.glob(port_path_template)

        if not detected_ports:
            return None

        if len(detected_ports) > 1:
            raise Arduino3AxisSerialMachineError(
                "Multiple USB serial ports attached: %s" %
                detected_ports
            )

        return detected_ports[0]

    @typechecked
    def initialize(self) -> None:
        """
        Please refer to the docstring in the base class.
        """
        self.guard_that_a_real_machine_is_connected()

        self._initialized = True
        self._ping_until_ok()

    @typechecked
    def _ping_until_ok(self) -> None:
        while True:
            self._ser.write(struct.pack('B', messages.MESSAGE_PING))
            time.sleep(0.1)
            content = self._ser.read_all()
            assert len(content) <= 1

            if content != b'':
                response, = struct.unpack('B', content)
                if response == messages.MESSAGE_PONG:
                    break

    @typechecked
    def flush(self) -> None:
        """
        Please refer to the docstring in the base class.
        """
        self.guard_that_a_real_machine_is_connected()

        self._ser.write(struct.pack('B', messages.MESSAGE_FLUSH))
        content = self._ser.read(1)
        response, = struct.unpack('B', content)
        if response != messages.MESSAGE_FLUSH_STARTED:
            raise MachineCommunicationException("Invalid response: %s when trying to FLUSH" % response)
        content = self._ser.read(1)
        response, = struct.unpack('B', content)
        if response == messages.MESSAGE_FLUSH_FINISHED:
            return
        elif response == messages.MESSAGE_FLUSH_FAILED:
            content = self._ser.read(1)
            raise MachineCommunicationException("Failed flush: %s" % content)
        else:
            raise MachineCommunicationException("Invalid response: %s when trying to FLUSH" % response)

    @typechecked
    def _set_dir(self, axis_id: int, state: int) -> None:
        if state == self._last_direction.get(axis_id, None):
            return
        self._last_direction[axis_id] = state

        self._ser.write(struct.pack('B', messages.MESSAGE_SET_DIR))
        self._ser.write(struct.pack('B', axis_id))
        self._ser.write(struct.pack('B', state))
        content = self._ser.read(1)
        response, = struct.unpack('B', content)
        if response != messages.MESSAGE_SET_DIR_SCHEDULED:
            raise MachineCommunicationException("Invalid response: %s when trying to SET_DIR %d %d" % (
                response,
                axis_id,
                state
            ))

    @typechecked
    def _three_pwm(self, time_us: int, steps_x: int, steps_y: int, steps_z: int) -> None:
        if steps_x == 0 and steps_y == 0 and steps_z == 0:
            return

        self._ser.write(struct.pack('B', messages.MESSAGE_THREE_PWM))
        self._ser.write(struct.pack('<I', time_us))
        self._ser.write(struct.pack('<I', steps_x))
        self._ser.write(struct.pack('<I', steps_y))
        self._ser.write(struct.pack('<I', steps_z))
        content = self._ser.read(1)
        response, = struct.unpack('B', content)
        if response != messages.MESSAGE_THREE_PWM_SCHEDULED:
            raise MachineCommunicationException("Invalid response: %s when trying to THREE_PWM %d %d %d %d" % (
                response,
                time_us,
                steps_x,
                steps_y,
                steps_z
            ))

    @typechecked
    def move_by(self, x: Numeric, y: Numeric, z: Numeric, feed_rate: Numeric) -> None:
        """
        Please refer to the docstring in the base class.
        """
        self.guard_that_a_real_machine_is_connected()

        if not self._initialized:
            raise MachineCommunicationException("Uninitialized machine")

        if (x < 0) ^ self._invert_x:
            self._set_dir(0, 0)
        else:
            self._set_dir(0, 1)

        if (y < 0) ^ self._invert_y:
            self._set_dir(1, 0)
        else:
            self._set_dir(1, 1)

        if (z < 0) ^ self._invert_z:
            self._set_dir(2, 0)
        else:
            self._set_dir(2, 1)

        x = abs(x)
        y = abs(y)
        z = abs(z)

        time_us = 1_000_000 * 60 * max(x, y, z) / feed_rate

        self._three_pwm(
            int(time_us),
            int(x * self._steps_per_mm_x),
            int(y * self._steps_per_mm_y),
            int(z * self._steps_per_mm_z)
        )

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
