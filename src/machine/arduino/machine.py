import binascii
import serial
import struct
import time

from machine.arduino import messages
from exceptions import MachineUseException

class Arduino3AxisSerialMachine:
    def __init__(
            self,
            port,
            steps_per_mm_x,
            steps_per_mm_y,
            steps_per_mm_z,
            invert_x,
            invert_y,
            invert_z,
            default_feed_rate,
            rapid_move_feed_rate):
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

    def initialize(self):
        self._initialized = True
        self._ping_until_ok()

    def _ping_until_ok(self):
        while True:
            self._ser.write(struct.pack('B', messages.MESSAGE_PING))
            time.sleep(0.1)
            content = self._ser.read_all()
            assert len(content) <= 1

            if content != b'':
                response, = struct.unpack('B', content)
                if response == messages.MESSAGE_PONG:
                    break

    def flush(self):
        self._ser.write(struct.pack('B', messages.MESSAGE_FLUSH))
        content = self._ser.read(1)
        response, = struct.unpack('B', content)
        if response != messages.MESSAGE_FLUSH_STARTED:
            raise MachineUseException("Invalid response: %s when trying to FLUSH" % response)
        content = self._ser.read(1)
        response, = struct.unpack('B', content)
        if response == messages.MESSAGE_FLUSH_FINISHED:
            return
        elif response == messages.MESSAGE_FLUSH_FAILED:
            content = self._ser.read(1)
            raise MachineUseException("Failed flush: %s" % content)
        else:
            raise MachineUseException("Invalid response: %s when trying to FLUSH" % response)

    def _set_dir(self, axis_id, state):
        if state == self._last_direction.get(axis_id, None):
            return
        self._last_direction[axis_id] = state

        self._ser.write(struct.pack('B', messages.MESSAGE_SET_DIR))
        self._ser.write(struct.pack('B', axis_id))
        self._ser.write(struct.pack('B', state))
        content = self._ser.read(1)
        response, = struct.unpack('B', content)
        if response != messages.MESSAGE_SET_DIR_SCHEDULED:
            raise MachineUseException("Invalid response: %s when trying to SET_DIR %d %d" % (
                response,
                axis_id,
                state
            ))

    def _three_pwm(self, time_us, steps_x, steps_y, steps_z):
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
            raise MachineUseException("Invalid response: %s when trying to THREE_PWM %d %d %d %d" % (
                response,
                time_us,
                steps_x,
                steps_y,
                steps_z
            ))

    def move_by(self, x, y, z, feed_rate):
        if not self._initialized:
            raise MachineUseException("Uninitialized machine")

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
    def default_feed_rate(self):
        return self._default_feed_rate

    @property
    def rapid_move_feed_rate(self):
        return self._rapid_move_feed_rate

