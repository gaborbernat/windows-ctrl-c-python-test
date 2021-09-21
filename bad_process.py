"""This is a non compliant process that does not listens to signals"""
import os
import signal
import sys
import time
from pathlib import Path
from types import FrameType

out = sys.stdout


def handler(signum: signal.Signals, _: FrameType) -> None:  # noqa: U101
    _p(f"how about no signal {signum!r}-{signal.Signals(signum).name}")


def _p(m: str) -> None:
    out.write(f"{m}{os.linesep}")
    out.flush()  # force output flush in case we get killed


_p(f"started {os.getpid()} {__name__} with {sys.argv!r}")
_p(f"Running {sys.executable} {sys.version_info}")
signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

try:
    start_file = Path(sys.argv[1])
    start_file.write_text("")
    _p(f"created {start_file}")
    while True:  # busy sleep to wait give chance for signal handler
        time.sleep(0.01)
finally:
    _p(f"done {__name__}")
