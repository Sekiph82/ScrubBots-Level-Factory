"""Atomic file replace that survives a brief reader on Windows."""
import os
import time


def replace(source, target, *, attempts: int = 40) -> None:
    """os.replace, retried while another process briefly has `target` open.

    On Windows os.replace onto an open file raises PermissionError (WinError 5).
    2026-11-13: the PNG batch coordinator died when the Studio's 2.5 s status read
    had the job file open at that moment. Waits up to ~18 s in total.
    """
    for attempt in range(attempts):
        try:
            os.replace(source, target)
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(min(0.05 * (attempt + 1), 0.5))
