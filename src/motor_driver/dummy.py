class DummyMotorDriver:
    def __init__(self, *unused_args, **unused_kwargs):
        pass

    def signal_go_left(self):
        self._raise()

    def signal_go_right(self):
        self._raise()

    def signal_pul_up(self):
        self._raise()

    def signal_pul_down(self):
        self._raise()

    def step_left(self, unused_step_time):
        self._raise()

    def step_right(self, unused_step_time):
        self._raise()

    def step(self, unused_step_time):
        self._raise()

    def _raise(self):
        raise NotImplementedError("No actual milling machine connected")
