from __future__ import annotations

import ast
from pathlib import Path
import subprocess

import pytest

from scrubbots_pixel_factory.compact_solver_state import (
    ACTIVE_BYTE,
    CLEARED_BYTE,
    COMPACT_STATE_SCHEMA,
    COMPACT_STATE_VERSION,
    AuthorityVerificationDisposition,
    CompactSolverState,
    CompactStateContractError,
    LevelIdentity,
    OccupiedSlot,
    PROOF_STATE_FIELDS,
    PROOF_STATE_SOURCE_PATH,
    SLOT_COUNT,
    SolverStateAuthority,
    SupplyBatch,
    verify_authority_checkout,
)


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "scrubbots_pixel_factory" / "compact_solver_state.py"
AUTHORITY_SHA = "1144704e6c3647ed1cf76c610be5bd675585734a"


def authority() -> SolverStateAuthority:
    return SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", AUTHORITY_SHA)


def level() -> LevelIdentity:
    return LevelIdentity("a" * 64, "level-test", 2, 2, 4)


def state() -> CompactSolverState:
    return CompactSolverState(
        authority=authority(),
        level=level(),
        active_mask=bytes((ACTIVE_BYTE, ACTIVE_BYTE, CLEARED_BYTE, ACTIVE_BYTE)),
        supply=((SupplyBatch("batch-a", 1, 2),), (SupplyBatch("batch-b", 2, 1),), (), ()),
        slots=(None, OccupiedSlot("slot-batch", 1, 2, 1, "ACTIVE"), None, None, None),
        next_seq=2,
        column_count=4,
        preview_depth=3,
        palette_size=4,
    )


def test_canonical_authority_and_proof_state_shape_are_locked() -> None:
    assert authority().canonical_dict() == {
        "schema": "scrubbots-proof-state-authority",
        "version": 1,
        "repository": "https://github.com/Sekiph82/Scrubbots",
        "commit_sha": AUTHORITY_SHA,
        "proof_state_source_path": PROOF_STATE_SOURCE_PATH,
    }
    assert PROOF_STATE_FIELDS == ("level", "active", "supply", "slots", "next_seq", "column_count", "preview_depth", "palette_size")
    assert SLOT_COUNT == 5 and ACTIVE_BYTE == 1 and CLEARED_BYTE == 0
    with pytest.raises(CompactStateContractError):
        SolverStateAuthority("https://example.invalid/game", AUTHORITY_SHA)
    with pytest.raises(CompactStateContractError):
        SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", "not-a-sha")
    with pytest.raises(CompactStateContractError):
        SolverStateAuthority("https://github.com/Sekiph82/Scrubbots", AUTHORITY_SHA, "../proof_state.gd")


def test_state_is_typed_immutable_and_source_bytes_are_copied() -> None:
    source = bytearray(b"level-data-source")
    identity = LevelIdentity.from_source_bytes(source, level_id="source", width=2, height=2)
    source[0] = ord("X")
    assert identity.source_sha256 == __import__("hashlib").sha256(b"level-data-source").hexdigest()
    compact = state()
    assert isinstance(compact.active_mask, bytes)
    assert isinstance(compact.supply, tuple) and isinstance(compact.slots, tuple)
    with pytest.raises((AttributeError, TypeError)):
        compact.next_seq = 3  # type: ignore[misc]


def test_deterministic_closed_serialization_round_trips_without_canonical_key_claim() -> None:
    compact = state()
    encoded = compact.canonical_bytes()
    restored = CompactSolverState.from_dict(compact.canonical_dict())
    assert encoded == restored.canonical_bytes()
    assert compact.digest() == restored.digest()
    assert compact.canonical_dict()["schema"] == COMPACT_STATE_SCHEMA
    assert compact.canonical_dict()["version"] == COMPACT_STATE_VERSION
    assert "canonical_key" not in dir(compact)
    assert "legal_action_columns" not in dir(compact)
    assert "is_solved" not in dir(compact)


def test_closed_schema_and_structural_malformed_inputs_fail_closed() -> None:
    payload = state().canonical_dict()
    cases = []
    cases.append({**payload, "unexpected": True})
    cases.append({**payload, "version": 99})
    cases.append({**payload, "active_mask_hex": "ff00ff00"})
    cases.append({**payload, "slots": [None]})
    cases.append({**payload, "supply": payload["supply"][:-1]})  # type: ignore[index]
    cases.append({**payload, "level": {**payload["level"], "cell_count": 3}})  # type: ignore[index]
    for malformed in cases:
        with pytest.raises(CompactStateContractError):
            CompactSolverState.from_dict(malformed)

    with pytest.raises(CompactStateContractError):
        CompactSolverState(authority(), level(), b"\x01\x02\x03\x01", ((), (), ()), (None,) * 5, 1, 3, 3, 4)
    with pytest.raises(CompactStateContractError):
        SupplyBatch("", 1, 1)
    with pytest.raises(CompactStateContractError):
        OccupiedSlot("slot", 1, -1, 0, "ACTIVE")


def test_supply_fifo_order_slot_shape_and_scalar_domains_are_preserved() -> None:
    compact = state()
    assert [batch.batch_id for batch in compact.supply[0]] == ["batch-a"]
    assert compact.slots[1] == OccupiedSlot("slot-batch", 1, 2, 1, "ACTIVE")
    assert compact.column_count == 4 and compact.preview_depth == 3 and compact.palette_size == 4
    payload = compact.canonical_dict()
    assert payload["supply"][0][0] == {"id": "batch-a", "color": 1, "count": 2}  # type: ignore[index]
    assert payload["slots"][1] == {"batch_id": "slot-batch", "color": 1, "remaining": 2, "seq": 1, "state": "ACTIVE"}  # type: ignore[index]


def test_authority_verification_fails_closed_on_unverified_checkout_without_path_identity(tmp_path: Path) -> None:
    missing = verify_authority_checkout(authority(), tmp_path / "missing")
    assert missing.disposition is AuthorityVerificationDisposition.UNAVAILABLE
    assert missing.observed_commit_sha is None
    assert "checkout" in missing.reason

    mismatch = verify_authority_checkout(authority(), ROOT)
    assert mismatch.disposition in {AuthorityVerificationDisposition.MISMATCH, AuthorityVerificationDisposition.UNAVAILABLE}
    assert "checkout_path" not in mismatch.canonical_dict()


def test_module_is_headless_data_only_and_has_no_future_transition_or_wfc_surface() -> None:
    source = SOURCE.read_text(encoding="utf-8").lower()
    tree = ast.parse(source)
    imported = {
        node.names[0].name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
    }
    imported.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    assert "wfc" not in source
    assert imported <= {"__future__", "dataclasses", "enum", "hashlib", "json", "os", "pathlib", "re", "subprocess", "typing"}
    method_names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "canonical_key" not in method_names
    for forbidden in ("legal_action", "apply_move", "quiesce", "target_selector", "routing", "difficulty_score", "search_state"):
        assert forbidden not in source


def test_headless_import_smoke() -> None:
    result = subprocess.run(
        ["python", "-c", "from scrubbots_pixel_factory.compact_solver_state import CompactSolverState; print('COMPACT_STATE_HEADLESS_OK')"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "COMPACT_STATE_HEADLESS_OK"
