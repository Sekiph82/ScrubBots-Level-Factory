"""P0-P S4: the long-lived Studio service answers JSON lines and exits when the Studio closes the pipe."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

LAUNCHER = Path(__file__).resolve().parents[2] / "level_factory" / "scripts" / "factory_core_launcher.py"


def _ask(process: subprocess.Popen, message: dict) -> dict:
    process.stdin.write((json.dumps(message) + "\n").encode())
    process.stdin.flush()
    return json.loads(process.stdout.readline())


def test_service_answers_in_order_refuses_writers_and_exits_with_the_pipe():
    # Arrange
    process = subprocess.Popen([sys.executable, "-B", str(LAUNCHER), "serve"],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        # Act / Assert: a read-only operation is answered with its id.
        options = _ask(process, {"id": 1, "operation": "provider-options", "request": {}})
        assert options["id"] == 1 and options["exit_code"] == 0 and isinstance(options["payload"], dict)
        # A writer is never served by the long-lived process.
        refused = _ask(process, {"id": 2, "operation": "png-batch-run", "request": {}})
        assert refused == {"id": 2, "served": False}  # the Studio runs it in its own process
        # A malformed line does not end the service.
        process.stdin.write(b"not json\n"); process.stdin.flush()
        assert json.loads(process.stdout.readline())["exit_code"] == 2
        assert _ask(process, {"id": 3, "operation": "provider-options", "request": {}})["id"] == 3
    finally:
        process.stdin.close()
    # Closing the pipe (Studio exit) ends the service.
    assert process.wait(timeout=30) == 0
