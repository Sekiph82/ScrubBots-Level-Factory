from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    Environment,
    StagingDownloadedPackEvidence,
    StagingDownloadReasonCode,
    StagingDownloadVerificationReceipt,
    StagingDownloadVerificationReport,
    verify_current_main_supply_replay,
)
from scrubbots_content_pipeline import current_main_replay as gate  # noqa: E402

AUTHORITY = {
    "repository": "Sekiph82/Scrubbots", "branch": "main", "commit": "1" * 40,
    "source_sha256": {path: "c" * 64 for path in gate.AUTHORITY_SOURCE_PATHS},
}
GAME_STATE: dict[str, object] = {}

LEVEL_ID = "level-fixture"
PACK_ID = "fixture-pack"
LEVEL_BYTES = b'{"id":"level-fixture"}'
PLAN = {
    "schema": "scrubbots.level_supply_plan.v1", "version": 1, "levelId": LEVEL_ID,
    "columnCount": 3, "visiblePreviewDepth": 3, "maxRobotsPerBatch": 2,
    "columns": [[{"batchId": f"batch-{index}", "cid": "C01", "robots": 1}] for index in range(3)],
}
PLAN_BYTES = json.dumps(PLAN, sort_keys=True, separators=(",", ":")).encode()
PACK_BYTES = b"immutable scrubpack bytes"
MANIFEST_BYTES = b"immutable manifest bytes"


def _report(pack_bytes: bytes = PACK_BYTES) -> StagingDownloadVerificationReport:
    pack = StagingDownloadedPackEvidence(
        PACK_ID, "packs/fixture.scrubpack", hashlib.sha256(pack_bytes).hexdigest(), len(pack_bytes), (LEVEL_ID,)
    )
    receipt = StagingDownloadVerificationReceipt(
        "1.0", MANIFEST_BYTES, hashlib.sha256(MANIFEST_BYTES).hexdigest(), len(MANIFEST_BYTES), 1,
        "manifests/current.json", Environment.STAGING.value, "staging:default", "provider", "1.0", "1.0",
        "capability", "1.0", "1.0.0", (), (), (pack,), ("a" * 64,), ("pack_hashes",),
    )
    return StagingDownloadVerificationReport(
        True, StagingDownloadReasonCode.VERIFIED, receipt, None, True, (PACK_ID,)
    )


def _configure(monkeypatch, *, levels: dict[str, tuple[bytes, bytes]] | None = None) -> dict[str, object]:
    binding = {
        "level_id": LEVEL_ID,
        "level_data_sha256": hashlib.sha256(LEVEL_BYTES).hexdigest(),
        "supply_plan_sha256": hashlib.sha256(PLAN_BYTES).hexdigest(),
        "fifo_columns": PLAN["columns"], "column_count": 3, "visible_preview_depth": 3,
        "max_robots_per_batch": 2, "solver_state_sha256": "a" * 64,
        "solver_evidence_sha256": "b" * 64,
        "authority": {"repository": "Sekiph82/Scrubbots", "branch": "main", "git_head": "1" * 40},
    }
    artifact = json.dumps({"schema": "scrubbots.scrubpack.solver-supply-identity-artifact.v1", "version": 1,
                          "pack_sha256": hashlib.sha256(PACK_BYTES).hexdigest(), "levels": [binding]}).encode()
    monkeypatch.setattr(gate, "inspect_scrubpack", lambda raw: type("Inspection", (), {
        "accepted": True, "pack_id": PACK_ID, "level_ids": (LEVEL_ID,),
    })())
    monkeypatch.setattr(gate, "verify_solver_proven_scrubpack", lambda *args: True)
    monkeypatch.setattr(gate, "serialize_staging_download_verification_receipt", lambda receipt: "valid fixture")
    monkeypatch.setattr(gate, "_inspect_pack_levels", lambda raw: levels or {LEVEL_ID: (LEVEL_BYTES, PLAN_BYTES)})
    output_row = {
        "accepted": True, "level_id": LEVEL_ID,
        "level_sha256": hashlib.sha256(LEVEL_BYTES).hexdigest(),
        "plan_sha256": hashlib.sha256(PLAN_BYTES).hexdigest(), "fifo_columns": PLAN["columns"],
        "solver_status": "SOLVED", "replay_ok": True, "replay_solved": True,
        "final_active": 0, "unresolved": 0, "supply_exhausted": True,
        "solver_state_sha256": "a" * 64, "solver_evidence_sha256": "b" * 64,
    }
    GAME_STATE["output"] = {"accepted": True, "levels": [output_row]}
    return {PACK_ID: artifact}


def _run(monkeypatch, *, report=None, manifest: bytes = MANIFEST_BYTES, pack: bytes = PACK_BYTES,
         artifacts: dict[str, bytes] | None = None, levels=None):
    if artifacts is None:
        artifacts = _configure(monkeypatch, levels=levels)
    def run_game(levels):
        error = GAME_STATE.pop("runner_error", None)
        if error is not None:
            raise error
        return GAME_STATE["output"]
    return gate.verify_current_main_supply_replay(
        staging_report=report or _report(), downloaded_manifest_bytes=manifest,
        downloaded_pack_bytes={PACK_ID: pack}, solver_identity_artifacts=artifacts,
        pack_build_evidence={PACK_ID: object()}, game_authority=AUTHORITY,
        authority_check=lambda: GAME_STATE.pop("authority_second", AUTHORITY),
        game_runner=run_game,
    )


def test_all_levels_require_exact_stage_bytes_identity_and_game_replay(monkeypatch) -> None:
    result = _run(monkeypatch)
    assert result.accepted and result.reason_code == "VERIFIED"
    assert result.target_environment == "STAGING"
    assert result.game_commit == "1" * 40
    assert result.pack_results[0]["pack_id"] == PACK_ID
    assert result.to_dict()["packs"][0]["levels"][0]["solver_status"] == "SOLVED"


def test_rejects_unverified_status_manifest_pack_and_missing_cpx_evidence(monkeypatch) -> None:
    _configure(monkeypatch)
    failed = replace(_report(), accepted=False, reason_code=StagingDownloadReasonCode.PACK_INVALID)
    assert _run(monkeypatch, report=failed).reason_code == "STAGING_DOWNLOAD_NOT_VERIFIED"
    assert _run(monkeypatch, manifest=b"altered manifest").reason_code == "MANIFEST_DIGEST_MISMATCH"
    assert _run(monkeypatch, pack=b"altered pack").reason_code == "STAGED_PACK_DIGEST_MISMATCH"
    assert _run(monkeypatch, artifacts={}).reason_code == "CPX001_EVIDENCE_MISSING"


def test_rejects_schema_level_and_cpx001_digest_mismatch_before_godot(monkeypatch) -> None:
    wrong_schema = dict(PLAN, schema="wrong")
    wrong_schema_bytes = json.dumps(wrong_schema, sort_keys=True, separators=(",", ":")).encode()
    artifacts = _configure(monkeypatch, levels={LEVEL_ID: (LEVEL_BYTES, wrong_schema_bytes)})
    artifact_doc = json.loads(artifacts[PACK_ID])
    artifact_doc["levels"][0]["supply_plan_sha256"] = hashlib.sha256(wrong_schema_bytes).hexdigest()
    artifact_doc["levels"][0]["fifo_columns"] = wrong_schema["columns"]
    artifacts[PACK_ID] = json.dumps(artifact_doc).encode()
    assert _run(monkeypatch, levels={LEVEL_ID: (LEVEL_BYTES, wrong_schema_bytes)}, artifacts=artifacts).reason_code == "CPX001_IDENTITY_MISMATCH"
    assert _run(monkeypatch, levels={"other-level": (LEVEL_BYTES, PLAN_BYTES)}).reason_code == "CPX001_LEVEL_SET_MISMATCH"
    monkeypatch.setattr(gate, "_inspect_pack_levels", lambda raw: {LEVEL_ID: (LEVEL_BYTES, PLAN_BYTES)})
    artifacts = _configure(monkeypatch)
    artifact_doc = json.loads(artifacts[PACK_ID])
    artifact_doc["levels"][0]["level_data_sha256"] = "d" * 64
    artifacts[PACK_ID] = json.dumps(artifact_doc).encode()
    assert _run(monkeypatch, artifacts=artifacts).reason_code == "CPX001_DIGEST_MISMATCH"


def test_loader_solver_replay_timeout_and_error_all_fail_closed(monkeypatch) -> None:
    artifacts = _configure(monkeypatch)
    monkeypatch.setitem(GAME_STATE, "output", {"accepted": False, "levels": []})
    assert _run(monkeypatch, artifacts=artifacts).reason_code == "GAME_REPLAY_REJECTED"
    for response in (
        {"accepted": True, "levels": []},
        {"accepted": True, "levels": [{"level_id": LEVEL_ID, "solver_status": "UNSOLVED"}]},
        {"accepted": True, "levels": [{"level_id": LEVEL_ID, "solver_status": "INCONCLUSIVE"}]},
        {"accepted": True, "levels": [{"level_id": LEVEL_ID, "solver_status": "ERROR"}]},
    ):
        monkeypatch.setitem(GAME_STATE, "output", response)
        assert not _run(monkeypatch, artifacts=artifacts).accepted
    monkeypatch.setitem(GAME_STATE, "runner_error", gate.CurrentMainReplayError("GAME_REPLAY_TIMEOUT"))
    assert _run(monkeypatch, artifacts=artifacts).reason_code == "GAME_REPLAY_TIMEOUT"


def test_replay_and_authority_drift_block_multi_level_receipt(monkeypatch) -> None:
    artifacts = _configure(monkeypatch)
    monkeypatch.setitem(GAME_STATE, "output", {"accepted": True, "levels": [{
        "accepted": True, "level_id": LEVEL_ID, "level_sha256": hashlib.sha256(LEVEL_BYTES).hexdigest(),
        "plan_sha256": hashlib.sha256(PLAN_BYTES).hexdigest(), "fifo_columns": PLAN["columns"],
        "solver_status": "SOLVED", "replay_ok": False, "replay_solved": False,
        "final_active": 1, "unresolved": 1, "supply_exhausted": False,
        "solver_state_sha256": "a" * 64, "solver_evidence_sha256": "b" * 64,
    }]})
    assert _run(monkeypatch, artifacts=artifacts).reason_code == "GAME_REPLAY_REJECTED"
    changed_authority = dict(AUTHORITY, commit="2" * 40)
    monkeypatch.setitem(GAME_STATE, "authority_second", changed_authority)
    monkeypatch.setitem(GAME_STATE, "output", {"accepted": True, "levels": [{
        "accepted": True, "level_id": LEVEL_ID, "level_sha256": hashlib.sha256(LEVEL_BYTES).hexdigest(),
        "plan_sha256": hashlib.sha256(PLAN_BYTES).hexdigest(), "fifo_columns": PLAN["columns"],
        "solver_status": "SOLVED", "replay_ok": True, "replay_solved": True,
        "final_active": 0, "unresolved": 0, "supply_exhausted": True,
        "solver_state_sha256": "a" * 64, "solver_evidence_sha256": "b" * 64,
    }]})
    assert _run(monkeypatch, artifacts=artifacts).reason_code == "STALE_GAME_AUTHORITY"
    changed_source_hashes = dict(AUTHORITY["source_sha256"])
    changed_source_hashes[gate.AUTHORITY_SOURCE_PATHS[0]] = "d" * 64
    monkeypatch.setitem(GAME_STATE, "authority_second", dict(AUTHORITY, source_sha256=changed_source_hashes))
    assert _run(monkeypatch, artifacts=artifacts).reason_code == "STALE_GAME_AUTHORITY"


def test_multi_level_pack_requires_a_pass_for_every_level(monkeypatch) -> None:
    second_id = "level-second"
    second_level = b'{"id":"level-second"}'
    second_plan = dict(PLAN, levelId=second_id)
    second_plan["columns"] = [
        [{"batchId": f"second-{index}", "cid": "C01", "robots": 1}]
        for index in range(3)
    ]
    second_plan_bytes = json.dumps(second_plan, sort_keys=True, separators=(",", ":")).encode()
    levels = {LEVEL_ID: (LEVEL_BYTES, PLAN_BYTES), second_id: (second_level, second_plan_bytes)}
    artifacts = _configure(monkeypatch, levels=levels)
    monkeypatch.setattr(gate, "inspect_scrubpack", lambda raw: type("Inspection", (), {
        "accepted": True, "pack_id": PACK_ID, "level_ids": (LEVEL_ID, second_id),
    })())
    artifact_doc = json.loads(artifacts[PACK_ID])
    binding = dict(artifact_doc["levels"][0])
    binding.update({
        "level_id": second_id,
        "level_data_sha256": hashlib.sha256(second_level).hexdigest(),
        "supply_plan_sha256": hashlib.sha256(second_plan_bytes).hexdigest(),
        "fifo_columns": second_plan["columns"],
        "authority": dict(AUTHORITY, git_head=AUTHORITY["commit"]),
    })
    artifact_doc["levels"].append(binding)
    artifacts[PACK_ID] = json.dumps(artifact_doc).encode()
    base_receipt = _report().receipt
    assert base_receipt is not None
    pack_row = replace(base_receipt.packs[0], level_ids=(LEVEL_ID, second_id))
    report = replace(_report(), receipt=replace(base_receipt, packs=(pack_row,)))

    first_row = dict(GAME_STATE["output"]["levels"][0])
    monkeypatch.setitem(GAME_STATE, "output", {"accepted": True, "levels": [first_row]})
    assert _run(monkeypatch, report=report, artifacts=artifacts).reason_code == "GAME_REPLAY_REJECTED"

    second_row = dict(first_row)
    second_row.update({
        "level_id": second_id,
        "level_sha256": hashlib.sha256(second_level).hexdigest(),
        "plan_sha256": hashlib.sha256(second_plan_bytes).hexdigest(),
        "fifo_columns": second_plan["columns"],
    })
    monkeypatch.setitem(GAME_STATE, "output", {"accepted": True, "levels": [first_row, second_row]})
    assert _run(monkeypatch, report=report, artifacts=artifacts).accepted
