from __future__ import annotations

import ast
from pathlib import Path
import subprocess
import sys

import pytest

from scrubbots_pixel_factory.simulation_boundary import (
    AuthorityDescriptor,
    BoundaryContractError,
    BoundaryDisposition,
    BridgeConfiguration,
    CanonicalGameplayBridge,
    REQUIRED_CANONICAL_SOURCE_PATHS,
    SimulationRequest,
)


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "scrubbots_pixel_factory" / "simulation_boundary.py"
AUTHORITY_SHA = "1144704e6c3647ed1cf76c610be5bd675585734a"


def _authority(sha: str = AUTHORITY_SHA) -> AuthorityDescriptor:
    return AuthorityDescriptor(
        repository="https://github.com/Sekiph82/Scrubbots",
        commit_sha=sha,
    )


def test_authority_metadata_is_exactly_repository_sha_and_bridge_bound() -> None:
    authority = _authority()
    changed = _authority("0" * 40)
    assert authority.canonical_dict()["source_paths"] == list(REQUIRED_CANONICAL_SOURCE_PATHS)
    assert authority.digest() != changed.digest()
    assert authority.bridge_version == "canonical-proof-kernel-bridge-v1"
    with pytest.raises(BoundaryContractError):
        AuthorityDescriptor("https://example.invalid/game", AUTHORITY_SHA)
    with pytest.raises(BoundaryContractError):
        AuthorityDescriptor("https://github.com/Sekiph82/Scrubbots", "not-a-sha")


def test_wfc_generation_solver_is_not_gameplay_authority() -> None:
    source = SOURCE.read_text(encoding="utf-8").lower()
    assert "wfc" not in source
    assert "generator" not in source
    assert "legal_move" not in source
    assert "compact_solver" not in source
    assert "gameplay" in source


def test_boundary_imports_headlessly_without_ui_render_provider_or_network_modules() -> None:
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    imported = {
        node.names[0].name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
    }
    imported.update(
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    assert imported <= {"__future__", "dataclasses", "enum", "hashlib", "json", "os", "pathlib", "re", "typing"}
    result = subprocess.run(
        [sys.executable, "-c", "from scrubbots_pixel_factory.simulation_boundary import CanonicalGameplayBridge; print('HEADLESS_OK')"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "HEADLESS_OK"


def test_missing_canonical_checkout_returns_unavailable_without_fabricated_result(tmp_path: Path) -> None:
    bridge = CanonicalGameplayBridge(BridgeConfiguration(checkout_path=str(tmp_path / "missing")))
    capability = bridge.capability(_authority())
    result = bridge.simulate(SimulationRequest(_authority(), b'{"version":1}'))
    assert capability.disposition is BoundaryDisposition.UNAVAILABLE
    assert result.disposition is BoundaryDisposition.UNAVAILABLE
    assert result.canonical_disposition is None
    assert "does not exist" in result.reason


def test_present_authority_sources_without_stable_bridge_remains_unavailable(tmp_path: Path) -> None:
    for relative in REQUIRED_CANONICAL_SOURCE_PATHS:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("authority fixture", encoding="utf-8")
    before = {path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    bridge = CanonicalGameplayBridge(BridgeConfiguration(checkout_path=str(tmp_path)))
    result = bridge.simulate(SimulationRequest(_authority(), b"canonical-level-data"))
    assert result.disposition is BoundaryDisposition.UNAVAILABLE
    assert "no stable configured headless proof-kernel bridge" in result.reason
    assert {path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()} == before


def test_malformed_authority_and_request_fail_closed() -> None:
    bridge = CanonicalGameplayBridge(BridgeConfiguration())
    capability = bridge.capability({"repository": "wrong"})
    result = bridge.simulate({"canonical_input_bytes": b"nope"})
    assert capability.disposition is BoundaryDisposition.ERROR
    assert result.disposition is BoundaryDisposition.ERROR
    assert len(capability.reason) <= 512
    with pytest.raises(BoundaryContractError):
        BridgeConfiguration(checkout_path="relative/path")


def test_repeated_capability_and_result_are_deterministic_and_input_is_immutable(tmp_path: Path) -> None:
    authority = _authority()
    payload = bytearray(b"immutable canonical level bytes")
    request = SimulationRequest(authority, payload)
    original = bytes(payload)
    bridge = CanonicalGameplayBridge(BridgeConfiguration(checkout_path=str(tmp_path)))
    first_capability = bridge.capability(authority)
    second_capability = bridge.capability(authority)
    first_result = bridge.simulate(request)
    second_result = bridge.simulate(request)
    assert payload == original
    assert request.canonical_input_bytes == original
    assert first_capability.canonical_bytes() == second_capability.canonical_bytes()
    assert first_result.canonical_bytes() == second_result.canonical_bytes()
    assert first_result.request_digest == request.digest()
    assert first_result.authority_digest == authority.digest()
    assert first_result.disposition is BoundaryDisposition.UNAVAILABLE


def test_boundary_does_not_define_future_solver_state_or_legal_move_contracts() -> None:
    source = SOURCE.read_text(encoding="utf-8").lower()
    forbidden = ("legal move provider", "solver state", "win condition", "lose condition", "target selector")
    assert all(marker not in source for marker in forbidden)
