import enum
import multiprocessing
import queue
import time
import traceback
import typing

from typeguard import typechecked

import config
import gcode_interpreter


class WorkerProcessAlreadyStartedException(Exception):
    """
    The machine process has already been started.
    """
    pass


class WorkerProcessLogItemLevel(enum.Enum):
    """
    Severities of messages returned by the process.
    """
    INFO = 'INFO'
    ERROR = 'ERROR'


class WorkerProcessMessage(enum.Enum):
    """
    Kinds of messages sent to the process.
    """
    INITIALIZE = 'INITIALIZE'
    GCODE = 'GCODE'


class WorkerProcess():
    """
    A separate process that is a wrapper around a connection to a machine.

    G-Code and initialization requests may be send and logs may be received back.
    """
    def __init__(self):
        self._started = False

    @staticmethod
    def create_and_start():
        worker_process = WorkerProcess()
        worker_process.start()
        return worker_process

    @typechecked
    def start(self) -> None:
        if self._started:
            raise WorkerProcessAlreadyStartedException("This particular worker process has already benn started")
        else:
            self._command_queue = multiprocessing.Queue()
            self._log_queue = multiprocessing.Queue()
            self._process = multiprocessing.Process(
                target=WorkerProcess._run,
                args=(self._command_queue, self._log_queue),
            )
            self._process.start()

    @typechecked
    def send_message_initialize(self) -> None:
        self._command_queue.put((WorkerProcessMessage.INITIALIZE, ''))

    @typechecked
    def send_message_gcode(self, gcode: str) -> None:
        self._command_queue.put((WorkerProcessMessage.GCODE, gcode))

    @typechecked
    def kill(self) -> None:
        self._process.terminate()
        self._started = False

    @typechecked
    def get_logs(self) -> typing.List[typing.Dict[str, str]]:
        result = []
        try:
            while True:
                result.append(self._log_queue.get_nowait())
        except queue.Empty:
            pass

        return result

    @staticmethod
    @typechecked
    def _run(command_queue: multiprocessing.Queue, log_queue: multiprocessing.Queue) -> None:
        machine = config.MACHINE

        while True:
            message, data = command_queue.get()

            try:
                if message == WorkerProcessMessage.INITIALIZE:
                    machine.initialize()
                    log_queue.put({
                        'level': WorkerProcessLogItemLevel.INFO.value,
                        'message': "Machine initialized successfully"
                    })
                elif message == WorkerProcessMessage.GCODE:
                    start_time = time.time()

                    gcode_interpreter.GCodeInterpreter(machine).run_gcode_string(data)
                    gcode_execution_time = time.time() - start_time

                    log_queue.put({
                        'level': WorkerProcessLogItemLevel.INFO.value,
                        'message': "gcode interpreted successfully, took %.02f seconds" % gcode_execution_time,
                    })
                else:
                    assert(False)
            except Exception as e:
                traceback.print_exc()
                log_queue.put({
                    'level': WorkerProcessLogItemLevel.ERROR.value,
                    'message': "%s" % str(e),
                })
