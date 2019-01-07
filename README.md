# A toy milling machine driver with a web interface
Disclaimer: this tool is not stable. If you want to get actual stuff done,
you may prefer to use different, production-ready milling machine software.

![Build status](https://travis-ci.com/kazetkazet/cnc.svg?branch=master)

## How to connect
This tool uses Raspberry PI GPIO pins to interface with stepper motor drivers.
The GPIO pin numbers for `DIR` and `PUL` stepper motor driver inputs for each
axis are described in `config.py`.

## Installation prerequisites
To run this tool, you need to install `python3` and `python3-virtualenv`.

You don't have to be on a Raspberry PI - without GPIO available, you will
still be able to play with the tool - but without any actual milling.

## How to run
To run the web interface, execute the following command:

```bash
./launch.sh
```

The interface will listen on http://127.0.0.1:5000/.

## How to check code style (via flake8)
To check the code style, execute the following command:

```bash
./run_flake8.sh
```

## How to run the tests
To run the tests, execute the following command:

```bash
./run_tests.sh
```
