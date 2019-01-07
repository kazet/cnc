# A toy milling machine driver with a web interface
Disclaimer: this tool is not stable. If you want to get actual stuff done,
you may prefer to use different, production-ready milling machine software.

## How to connect
This tool uses Raspberry PI GPIO pins to interface with stepper motor drivers.
The GPIO pin numbers for `DIR` and `PUL` stepper motor driver inputs for each
axis are described in `config.py`.

## Installation prerequisites
To run this tool, you need to install `python3` and `python3-virtualenv`.

## How to run
To run the web interface, execute the following commands:

```bash
./launch.sh
```

The interface will listen on http://0.0.0.0:5000/.

## How to check code quality (via flake8)
To check the code quality, execute the following command:

```bash
./run_flake8.sh
```

## How to run the tests
To run the tests, execute the following command:

```bash
./run_tests.sh
```
