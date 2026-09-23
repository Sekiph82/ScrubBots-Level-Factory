from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess

import pytest

from scrubbots_pixel_factory.canonical_bridge import CANONICAL_BRIDGE_RUNNER_SHA256


ROOT = Path(__file__).resolve().parents[2]
RUNNER = Path("tools/scrubbots_canonical_bridge_runner.gd")


@pytest.mark.skipif(os.name != "nt", reason="Windows checkout-byte portability regression")
def test_windows_style_clean_local_clone_preserves_runner_identity(tmp_path: Path) -> None:
    checkout = tmp_path / "level-factory-windows-style"
    subprocess.run(
        ["git", "clone", "--local", "--no-hardlinks", str(ROOT), str(checkout)],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "-C", str(checkout), "config", "core.autocrlf", "true"], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(checkout), "config", "core.eol", "crlf"], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(checkout), "checkout", "--force", "--detach", "HEAD"], check=True, capture_output=True, text=True)

    runner = checkout / RUNNER
    materialized = runner.read_bytes()
    committed = subprocess.run(
        ["git", "show", f"HEAD:{RUNNER.as_posix()}"],
        cwd=checkout,
        check=True,
        capture_output=True,
    ).stdout
    attr = subprocess.run(
        ["git", "check-attr", "eol", "--", RUNNER.as_posix()],
        cwd=checkout,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=checkout,
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    assert attr.endswith("eol: lf")
    assert materialized == committed
    assert hashlib.sha256(materialized).hexdigest() == CANONICAL_BRIDGE_RUNNER_SHA256
    assert status == ""
