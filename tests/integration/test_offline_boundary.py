import os
import re
import socket
import subprocess
import sys
from pathlib import Path

import pytest

from scrubbots_pixel_factory import (
    OfflinePolicyError,
    deterministic_digest,
    guarded_network_request,
    offline_runtime,
)


REPO_ROOT = Path(__file__).parents[2]
SRC_ROOT = REPO_ROOT / "src"


def test_explicit_network_request_contract_remains_denied() -> None:
    with pytest.raises(OfflinePolicyError, match="offline-only"):
        guarded_network_request("https://example.invalid/generation")


def test_direct_socket_connect_is_denied_inside_production_boundary() -> None:
    with offline_runtime():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            with pytest.raises(OfflinePolicyError, match="offline-only"):
                sock.connect(("203.0.113.1", 9))


def test_create_connection_is_denied_inside_production_boundary() -> None:
    with offline_runtime():
        with pytest.raises(OfflinePolicyError, match="offline-only"):
            socket.create_connection(("203.0.113.1", 9), timeout=0.01)


def test_socket_symbols_are_restored_and_local_work_is_allowed() -> None:
    original_socket = socket.socket
    original_create_connection = socket.create_connection
    with offline_runtime():
        assert deterministic_digest("offline-local-work") == deterministic_digest(
            "offline-local-work"
        )
        assert socket.socket is not original_socket
        assert socket.create_connection is not original_create_connection
    assert socket.socket is original_socket
    assert socket.create_connection is original_create_connection


def test_import_performs_no_network_initialization() -> None:
    code = """
import sys

def deny_network_audit(event, _args):
    if event.startswith(("socket.", "http.")):
        raise AssertionError(f"network initialization during import: {event}")

sys.addaudithook(deny_network_audit)
import scrubbots_pixel_factory
assert scrubbots_pixel_factory.OFFLINE_ONLY is True
print(scrubbots_pixel_factory.__version__)
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_ROOT)
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "0.1.0"


def test_production_source_has_no_network_imports_outside_boundary() -> None:
    forbidden = re.compile(
        r"^\s*(?:from\s+(?:socket|urllib(?:\.|\b)|http(?:\.|\b)|httpx\b|requests\b|aiohttp\b)|"
        r"import\s+(?:socket\b|urllib\b|http\b|httpx\b|requests\b|aiohttp\b))",
        re.MULTILINE,
    )
    for source_path in SRC_ROOT.rglob("*.py"):
        if source_path.name == "offline.py":
            continue
        assert forbidden.search(source_path.read_text(encoding="utf-8")) is None, source_path


def test_standalone_import_does_not_depend_on_main_scrubbots_checkout() -> None:
    code = """
import scrubbots_pixel_factory
from pathlib import Path

module_path = Path(scrubbots_pixel_factory.__file__).resolve()
assert module_path.is_relative_to(Path.cwd() / "src")
print(module_path)
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_ROOT)
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert str(SRC_ROOT) in result.stdout
