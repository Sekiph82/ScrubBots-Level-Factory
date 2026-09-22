from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from scrubbots_pixel_factory.canonical_bridge import CanonicalBridgeConfiguration, CanonicalBridgeDisposition, CanonicalBridgeRequest, CanonicalHeadlessBridge
from scrubbots_pixel_factory.compact_solver_state import SolverStateAuthority


AUTHORITY = SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", "1144704e6c3647ed1cf76c610be5bd675585734a")
LEVEL_SHA = hashlib.sha256(b"fixture-LevelData-source").hexdigest()
STATE_SHA = hashlib.sha256(b"fixture-compact-state").hexdigest()


def test_unconfigured_production_adapter_is_truthfully_unavailable() -> None:
    bridge = CanonicalHeadlessBridge(CanonicalBridgeConfiguration(checkout_path=None, runner_path=None))
    capability = bridge.capability(AUTHORITY)
    assert capability.disposition is CanonicalBridgeDisposition.UNAVAILABLE
    assert "UNAVAILABLE" in capability.reason
    result = bridge.invoke(CanonicalBridgeRequest(AUTHORITY, "legal_moves", b"{}", STATE_SHA, LEVEL_SHA))
    assert result.disposition is CanonicalBridgeDisposition.UNAVAILABLE
    assert result.request_digest is not None
    assert result.result is None


def test_request_identity_is_immutable_and_deterministic() -> None:
    first = CanonicalBridgeRequest(AUTHORITY, "legal_moves", b"{}", STATE_SHA, LEVEL_SHA)
    second = CanonicalBridgeRequest(AUTHORITY, "legal_moves", b"{}", STATE_SHA, LEVEL_SHA)
    assert first.digest() == second.digest()
    assert first.runner_payload()["request_digest"] == first.digest()
    try:
        first.operation = "solver"  # type: ignore[misc]
    except AttributeError:
        pass
    else:
        raise AssertionError("bridge request must be immutable")


def test_malformed_authority_and_payload_fail_closed() -> None:
    bridge = CanonicalHeadlessBridge()
    assert bridge.capability(object()).disposition is CanonicalBridgeDisposition.ERROR
    assert bridge.invoke(object()).disposition is CanonicalBridgeDisposition.ERROR
    try:
        CanonicalBridgeRequest(AUTHORITY, "legal_moves", b"{}", "not-a-digest", LEVEL_SHA)
    except ValueError:
        pass
    else:
        raise AssertionError("malformed request digest must be rejected")


@pytest.mark.skipif(not os.environ.get("SCRUBBOTS_CANONICAL_CHECKOUT") or not os.environ.get("SCRUBBOTS_CANONICAL_BRIDGE_RUNNER"), reason="canonical checkout and external bridge runner capability were not supplied")
def test_real_canonical_capability_and_runner_are_capability_gated() -> None:
    checkout = Path(os.environ["SCRUBBOTS_CANONICAL_CHECKOUT"]).resolve()
    runner = Path(os.environ["SCRUBBOTS_CANONICAL_BRIDGE_RUNNER"]).resolve()
    before_status = __import__("subprocess").run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=checkout, capture_output=True, text=True, check=False).stdout
    before_source = (checkout / "scripts/gameplay/solver/proof_state.gd").read_bytes()
    bridge = CanonicalHeadlessBridge(CanonicalBridgeConfiguration(str(checkout), str(runner)))
    capability = bridge.capability(AUTHORITY)
    assert capability.disposition is CanonicalBridgeDisposition.AVAILABLE
    after_status = __import__("subprocess").run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=checkout, capture_output=True, text=True, check=False).stdout
    after_source = (checkout / "scripts/gameplay/solver/proof_state.gd").read_bytes()
    assert before_status == after_status
    assert before_source == after_source


def test_bridge_module_does_not_implement_gameplay_or_wfc() -> None:
    source = (Path(__file__).resolve().parents[2] / "src" / "scrubbots_pixel_factory" / "canonical_bridge.py").read_text(encoding="utf-8").lower()
    assert "apply_placement" not in source
    assert "legal_action_columns" not in source
    assert "canonical_key" not in source
    assert "wfc" not in source
