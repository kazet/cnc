import multiprocessing
import queue
import time

import config
import gcode


class WorkerProcessMessage():
    INITIALIZE = 'INITIALIZE'
    GCODE = 'GCODE'


def worker_process(command_queue, log_queue):
    while True:
        message, data = command_queue.get()

        if message == WorkerProcessMessage.INITIALIZE:
            config.MACHINE.initialize()
            log_queue.put("Machine initialized successfully")
        elif message == WorkerProcessMessage.GCODE:
            try:
                start_time = time.time()
                gcode.interpret(data)
                gcode_execution_time = time.time() - start_time

                log_queue.put(
                    "gcode interpreted successfully, took %.02f seconds" %
                    gcode_execution_time,
                )
            except Exception as e:
                log_queue.put("Unable to execute gcode: %s" % repr(e))
        else:
            assert(False)


def spawn_worker_process():
    command_queue = multiprocessing.Queue()
    log_queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=worker_process, args=(command_queue, log_queue))
    process.start()

    return process, command_queue, log_queue


def send_message_initialize():
    WORKER_COMMAND_QUEUE.put((WorkerProcessMessage.INITIALIZE, ''))


def send_message_gcode(gcode):
    WORKER_COMMAND_QUEUE.put((WorkerProcessMessage.GCODE, gcode))


def kill():
    WORKER_PROCESS.terminate()


def get_logs():
    result = ''
    try:
        while True:
            result += WORKER_LOG_QUEUE.get_nowait() + '\n'
    except queue.Empty:
        pass

    return result


WORKER_PROCESS, WORKER_COMMAND_QUEUE, WORKER_LOG_QUEUE = spawn_worker_process()
