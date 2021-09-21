import os
import sys
from pathlib import Path
from signal import CTRL_BREAK_EVENT, CTRL_C_EVENT, SIGINT, SIGTERM, Signals, getsignal, signal
from subprocess import CREATE_NEW_PROCESS_GROUP, PIPE, Popen
from threading import Thread
from time import sleep

HERE = Path(__file__).parent

count = 0


def exit_gracefully(signum, frame):
    global count
    print(f"ROOT {count} got {signum!r}-{Signals(signum).name}")
    if count < 3:
        print(f"ROOT {count} send CTRL_C_EVENT")
        thread.process.send_signal(SIGTERM)
    else:
        print(f"ROOT {count} send terminate")
        thread.process.kill()
    count += 1
    signal(SIGINT, exit_gracefully)


original_sigint = getsignal(SIGINT)
signal(SIGINT, exit_gracefully)


class Run(Thread):
    process: Popen

    def __init__(self):
        super().__init__()
        self.mark = HERE / "mark"
        if self.mark.exists():
            self.mark.unlink()

    def run(self) -> None:
        cmd = [sys.executable, str(HERE / "bad_process.py"), str(self.mark)]
        self.process = Popen(cmd, creationflags=CREATE_NEW_PROCESS_GROUP)
        self.process.communicate()
        print(f"process {self.process.pid} terminated with {self.process.returncode}")

    def wait(self):
        while not self.mark.exists():
            sleep(0.05)
        print("READY!")


thread = Run()
try:
    thread.start()
    thread.wait()
finally:
    print(f"join thread from {os.getpid()}")
    try:
        while True:
            thread.join(timeout=0.1)  # need to periodically wake up to give chance to the signal handler
            if not thread.is_alive():
                break
        print("Joined")
    finally:
        print("Exiting")
