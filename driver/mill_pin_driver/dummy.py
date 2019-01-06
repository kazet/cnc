class DummyMillPinDriver:
    def output(self, pin, value):
        raise NotImplementedError("No actual milling machine connected")
