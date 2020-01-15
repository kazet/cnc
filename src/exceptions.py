class MachineCommunicationException(Exception):
    """
    A generic exception that there was a problem with communicating with the machine.
    """
    def __init__(self, message):
        self.message = message
