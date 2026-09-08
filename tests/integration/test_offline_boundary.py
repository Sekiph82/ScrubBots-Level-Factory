import os
import subprocess
import sys
from pathlib import Path

import pytest

from scrubbots_pixel_factory import OfflinePolicyError, guarded_network_request


REPO_ROOT = Path(__file__).parents[2]
SRC_ROOT = REPO_ROOT / "src"


def test_protected_production_path_denies_deliberate_network_attempt() -> None:
    with pytest.raises(OfflinePolicyError, match="offline-only"):
        guarded_network_request("https://example.invalid/generation")


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
