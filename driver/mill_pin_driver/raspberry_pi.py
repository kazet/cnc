import time
import RPi.GPIO

class RaspberryPiMillPinDriver:
    MOTOR_PINS = {
        'X': {
            'DIR': 35,
            'PUL': 37,
        },
        'Y': {
            'DIR': 33,
            'PUL': 31,
        },
        'Z': {
            'DIR': 36,
            'PUL': 38,
        },
    }

    def __init__(self):
        self._configure_gpio()

    def _configure_gpio(self):
        RPi.GPIO.setmode(RPi.GPIO.BOARD)

        for motor_pin_dict in self.MOTOR_PINS.values():
            for output_pin_id in motor_pin_dict.values():
                RPi.GPIO.setup(output_pin_id, RPi.GPIO.OUT)

    def output(self, pin, value):
        RPi.GPIO.output(pin, value)