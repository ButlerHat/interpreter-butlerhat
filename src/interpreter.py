"""
Interpreter manager.
"""
import os
import sys
import uuid
import threading
import tempfile
from io import StringIO
from dataclasses import dataclass
from typing import Dict, IO, cast
from robotframework_interactive.interpreter import RobotFrameworkInterpreter
from robotframework_interactive.server.rf_interpreter_ls_config import (
        RfInterpreterRobotConfig,
    )

USE_TIMEOUTS = True
if "GITHUB_WORKFLOW" not in os.environ:
    if "pydevd" in sys.modules:
        USE_TIMEOUTS = False

@dataclass
class _InterpreterInfo:
    interpreter: RobotFrameworkInterpreter
    stream_stdout: StringIO
    stream_stderr: StringIO
    finish_main_loop_event: threading.Event
    finished_main_loop_event: threading.Event


class InterpreterManager:
    """
    Class for managing interpreters.
    """

    def __init__(self, max_interpreters: int = -1):
        self.interpreters: Dict[str, _InterpreterInfo] = {}
        self.max_interpreters = max_interpreters

    def __contains__(self, interpreter_id: str) -> bool:
        return interpreter_id in self.interpreters.keys()
    
    def get_info(self, interpreter_id: str) -> _InterpreterInfo:
        return self.interpreters[interpreter_id]
    
    def set_max_interpreters(self, max_interpreters: int):
        self.max_interpreters = max_interpreters

    def start_interpreter(self) -> str:
        """
        Start the interpreter and return interpreter id.
        """
        if self.max_interpreters > 0 and len(self.interpreters) >= self.max_interpreters:
            raise ValueError("Maximum number of interpreters reached")
        
        interpreter = RobotFrameworkInterpreter(RfInterpreterRobotConfig())  # type: ignore

        # Create temporary files for stdout and stderr
        stream_stdout: IO[str] = StringIO()
        stream_stderr: IO[str] = StringIO()

        def on_stdout(msg: str):
            print("Stdout: " + msg)
            stream_stdout.write(msg)
            stream_stdout.flush()

        def on_stderr(msg: str):
            print("Stderr: " + msg)
            stream_stderr.write(msg)
            stream_stderr.flush()

        interpreter.on_stdout.register(on_stdout)
        interpreter.on_stderr.register(on_stderr)

        started_main_loop_event = threading.Event()
        finish_main_loop_event = threading.Event()
        finished_main_loop_event = threading.Event()

        def run_on_thread():
            def on_main_loop(interpreter: RobotFrameworkInterpreter):  # pylint: disable=unused-argument
                started_main_loop_event.set()
                finish_main_loop_event.wait()
                finished_main_loop_event.set()

            interpreter.initialize(on_main_loop)  # type: ignore

        t = threading.Thread(target=run_on_thread)
        t.start()
        started_main_loop_event.wait(5 if USE_TIMEOUTS else None)

        interpreter_info = _InterpreterInfo(
            interpreter,
            stream_stdout,
            stream_stderr,
            finish_main_loop_event,
            finished_main_loop_event
        )

        # Generate a unique id and store the interpreter info in the dictionary
        interpreter_id = str(uuid.uuid4())
        self.interpreters[interpreter_id] = interpreter_info

        return interpreter_id

    def evaluate(self, interpreter_id: str, command: str) -> dict:
        """
        Evaluate the command in the interpreter with the given id.
        """
        if interpreter_id not in self.interpreters:
            raise ValueError(f"No interpreter found for id {interpreter_id}")

        interpreter_info = self.interpreters[interpreter_id]
        result_dict: dict = cast(dict, interpreter_info.interpreter.evaluate(command))
        result_dict["stdout"] = interpreter_info.stream_stdout.getvalue()
        return result_dict
            

    def stop_interpreter(self, interpreter_id: str):
        """
        Stop the interpreter with the given id.
        """
        if interpreter_id not in self.interpreters:
            raise ValueError(f"No interpreter found for id {interpreter_id}")

        self.interpreters[interpreter_id].finish_main_loop_event.set()
        self.interpreters[interpreter_id].finished_main_loop_event.wait(5 if USE_TIMEOUTS else None)
        del self.interpreters[interpreter_id]
