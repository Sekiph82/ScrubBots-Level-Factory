"""Small cooperative shutdown checks for Factory Studio-owned processes."""

from __future__ import annotations

import os
import signal
import subprocess
import time
from pathlib import Path
from collections.abc import Mapping, Sequence


def _owner_process_is_alive(raw_pid: str) -> bool:
    try:
        pid = int(raw_pid)
    except (TypeError, ValueError):
        return True
    if pid <= 0:
        return True
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        synchronize = 0x00100000
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel32.WaitForSingleObject.restype = wintypes.DWORD
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
        handle = kernel32.OpenProcess(synchronize, False, pid)
        if not handle:
            return ctypes.get_last_error() == 5  # Access denied: process may still be alive.
        try:
            wait_result = kernel32.WaitForSingleObject(handle, 0)
            return wait_result == 0x00000102  # WAIT_TIMEOUT
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def studio_shutdown_requested() -> bool:
    """Return true after Studio requests close or its owning process exits."""
    marker_path = os.environ.get("SCRUBBOTS_FACTORY_STUDIO_CANCEL_FILE", "").strip()
    if marker_path:
        try:
            if Path(marker_path).read_text(encoding="utf-8").strip() == "CANCEL_NOW":
                return True
        except FileNotFoundError:
            pass
        except (OSError, UnicodeError):
            # An unreadable signal must not let long-running paid/provider work continue.
            return True
    owner_pid = os.environ.get("SCRUBBOTS_FACTORY_STUDIO_PID", "").strip()
    return bool(owner_pid) and not _owner_process_is_alive(owner_pid)


def terminate_studio_child_tree(process: subprocess.Popen[object]) -> None:
    """Stop only a child process explicitly launched and held by this Studio worker."""
    if process.poll() is not None:
        return
    if os.name == "nt":
        taskkill = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "taskkill.exe"
        if taskkill.is_file():
            for wait_seconds in (5, 2):
                try:
                    subprocess.run(
                        [str(taskkill), "/PID", str(process.pid), "/T", "/F"],
                        capture_output=True, text=True, timeout=5, check=False,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                    )
                    process.wait(timeout=wait_seconds)
                    return
                except subprocess.TimeoutExpired:
                    continue
                except OSError:
                    break
        process.kill()
        process.wait()
        return

    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    except OSError:
        process.terminate()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, OSError):
            process.kill()
        process.wait()


class StudioShutdownRequested(RuntimeError):
    """Raised when a Studio-owned child is stopped during window shutdown."""


def run_studio_child_interruptibly(
    args: Sequence[str],
    *,
    cwd: str | os.PathLike[str] | None = None,
    env: Mapping[str, str] | None = None,
    timeout: float | None = None,
    poll_interval: float = 0.25,
    check_shutdown: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run one owned child while observing Studio shutdown and stop its PID tree."""
    if check_shutdown and studio_shutdown_requested():
        raise StudioShutdownRequested("Factory Studio is closing; child process was not started.")
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    if os.name == "nt":
        flags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    process = subprocess.Popen(
        list(args), cwd=cwd, env=dict(env) if env is not None else None,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        encoding="utf-8", errors="replace", creationflags=flags,
        start_new_session=(os.name != "nt"),
    )
    deadline = None if timeout is None else time.monotonic() + max(0.0, timeout)
    while True:
        if check_shutdown and studio_shutdown_requested():
            terminate_studio_child_tree(process)
            try:
                process.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                for stream in (process.stdout, process.stderr):
                    if stream is not None:
                        stream.close()
            raise StudioShutdownRequested("Factory Studio closed; its child process tree was stopped.")
        remaining = None if deadline is None else deadline - time.monotonic()
        if remaining is not None and remaining <= 0:
            terminate_studio_child_tree(process)
            try:
                stdout, stderr = process.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                stdout, stderr = "", ""
            raise subprocess.TimeoutExpired(args, timeout, output=stdout, stderr=stderr)
        interval = poll_interval if remaining is None else min(poll_interval, max(0.01, remaining))
        try:
            stdout, stderr = process.communicate(timeout=interval)
            return subprocess.CompletedProcess(args, int(process.returncode or 0), stdout, stderr)
        except subprocess.TimeoutExpired:
            continue


__all__ = ["StudioShutdownRequested", "run_studio_child_interruptibly", "studio_shutdown_requested", "terminate_studio_child_tree"]
