from __future__ import annotations

import sys
import threading
from collections import deque
from typing import Optional, TextIO, List


_lock = threading.Lock()
_buf: deque[str] = deque(maxlen=5000)
_installed = False


def add_line(line: str) -> None:
    line = line.rstrip("\r\n")
    if not line:
        return
    with _lock:
        _buf.append(line)


def get_lines(limit: int = 500) -> List[str]:
    if limit <= 0:
        return []
    with _lock:
        if len(_buf) <= limit:
            return list(_buf)
        return list(_buf)[-limit:]


class _CaptureStream:
    def __init__(self, underlying: Optional[TextIO], name: str):
        self._underlying = underlying
        self._name = name
        self._partial = ""

    @property
    def encoding(self) -> str:  # for compatibility
        try:
            return getattr(self._underlying, "encoding", "utf-8") or "utf-8"
        except Exception:
            return "utf-8"

    def isatty(self) -> bool:
        return False

    def write(self, s: str) -> int:
        if not isinstance(s, str):
            s = str(s)

        data = self._partial + s
        lines = data.split("\n")
        self._partial = lines.pop() if lines else ""

        for ln in lines:
            ln = ln.rstrip("\r")
            add_line(ln)

        if self._underlying:
            try:
                return self._underlying.write(s)
            except Exception:
                # swallow output errors (common when console is hidden / closed)
                return len(s)

        return len(s)

    def flush(self) -> None:
        if self._underlying:
            try:
                self._underlying.flush()
            except Exception:
                pass


def install_stdio_capture(forward: bool = True) -> None:
    """Capture stdout/stderr into an in-memory ring buffer.

    If forward is True, also forward output to the original streams.
    """

    global _installed
    if _installed:
        return

    out = sys.stdout if forward else None
    err = sys.stderr if forward else None

    sys.stdout = _CaptureStream(out, "stdout")  # type: ignore[assignment]
    sys.stderr = _CaptureStream(err, "stderr")  # type: ignore[assignment]

    _installed = True
