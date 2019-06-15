class SimulatedMachine:
    def __init__(self):
        self._simulated_moves = [(0, 0, 0)]
        self._default_feed_rate = 1
        self._rapid_move_feed_rate = 10
        self._tool_position_x = 0
        self._tool_position_y = 0
        self._tool_position_z = 0

    def flush(self):
        pass

    def move_by(self, x, y, z, feed_rate):
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
    def simulated_moves(self):
        return self._simulated_moves

    @property
    def default_feed_rate(self):
        return self._default_feed_rate

    @property
    def rapid_move_feed_rate(self):
        return self._rapid_move_feed_rate
