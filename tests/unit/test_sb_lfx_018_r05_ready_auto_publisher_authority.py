from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import pytest
import scrubbots_publish_handoff as handoff
from scrubbots_pixel_factory import studio_extensions as studio
from scrubbots_pixel_factory.supply_pipeline import release_pool, scrubpack_identity


SHA = "a" * 40
AUTHORITY = {"repository": "Sekiph82/Scrubbots", "branch": "main", "commit": SHA}


def _entry(candidate_id: str = "candidate-ready-auto", **overrides):
    pipeline = {
        "candidate_id": candidate_id,
        "run_id": "pipeline-ready-auto",
        "disposition": "READY",
        "primary": {"state": "READY", "disposition": "READY"},
    }
    value = {
        "schema": "scrubbots-release-pool-entry/v1",
        "candidate_id": candidate_id,
        "eligibility_source": "READY_AUTO",
        "review_id": None,
        "pipeline_run_id": pipeline["run_id"],
        "pipeline_sha256": "b" * 64,
        "pipeline": pipeline,
    }
    value.update(overrides)
    return value


def test_ready_auto_is_valid_only_with_consistent_release_pool_authority():
    valid = _entry()
    assert handoff._valid_pool_entry(valid)
    assert not handoff._valid_pool_entry({**valid, "review_id": "invented-review"})
    assert not handoff._valid_pool_entry({**valid, "eligibility_source": "UNKNOWN"})
    assert not handoff._valid_pool_entry({**valid, "pipeline_sha256": "bad"})
    assert not handoff._valid_pool_entry({**valid, "pipeline": {**valid["pipeline"], "primary": {"state": "UNAVAILABLE"}}})

    assert release_pool._eligibility_matches_current_review(valid, None)
    assert not release_pool._eligibility_matches_current_review(valid, {"disposition": "REJECT"})
    accepted = _entry(eligibility_source="OWNER_ACCEPT", review_id="review-current")
    assert release_pool._eligibility_matches_current_review(accepted, {
        "disposition": "ACCEPT", "review_id": "review-current"})
    assert not release_pool._eligibility_matches_current_review(accepted, {
        "disposition": "ACCEPT", "review_id": "review-stale"})


def test_ready_auto_preflight_requires_explicit_candidate_selection(monkeypatch):
    entry = _entry()
    monkeypatch.setattr(handoff, "_next_content_version", lambda: 7)
    request = {
        "candidate_ids": [entry["candidate_id"]], "pack_id": "first-family-pack",
        "content_version": 7, "created_at_utc": "2026-10-12T09:00:00Z",
    }
    result = handoff.publish_preflight(
        request, release_pool_reader=lambda: (entry,),
        pack_builder=lambda *_args, **_kwargs: SimpleNamespace(evidence=SimpleNamespace(
            level_ids=("level-1",), pack_id="first-family-pack",
            archive_sha256="c" * 64, archive_byte_length=1234)),
        game_authority_reader=lambda: AUTHORITY,
    )
    assert result["state"] == "PREFLIGHT_READY"
    assert result["mutation_performed"] is False
    assert result["candidate_ids"] == [entry["candidate_id"]]

    unselected = handoff.publish_preflight(
        {**request, "candidate_ids": ["another-candidate"]},
        release_pool_reader=lambda: (entry,),
        game_authority_reader=lambda: AUTHORITY,
    )
    assert unselected["state"] == "AWAITING_OWNER_RELEASE_BATCH"
    assert unselected["mutation_performed"] is False


def test_final_solver_proof_revalidation_accepts_ready_auto_but_honors_reject(monkeypatch):
    level_bytes = b"level-data"
    supply_bytes = b"supply-plan"
    paths = {"virtual/level.json": level_bytes, "virtual/supply.json": supply_bytes}
    monkeypatch.setattr(Path, "read_bytes", lambda path: paths[str(path).replace("\\", "/")])
    candidate_id = "candidate-ready-auto"
    pipeline = {
        "candidate_id": candidate_id, "run_id": "pipeline-ready-auto",
        "disposition": "READY",
        "primary": {"state": "READY", "disposition": "READY", "files": {
            "level": "virtual/level.json", "supply_plan": "virtual/supply.json"}},
    }
    pipeline_bytes = json.dumps(pipeline, sort_keys=True, separators=(",", ":")).encode()
    entry = {
        **_entry(candidate_id),
        "pipeline_sha256": hashlib.sha256(pipeline_bytes).hexdigest(),
        "files": {
            "level": {"path": "virtual/level.json", "sha256": hashlib.sha256(level_bytes).hexdigest()},
            "supply_plan": {"path": "virtual/supply.json", "sha256": hashlib.sha256(supply_bytes).hexdigest()},
        },
    }
    entry.pop("entry_digest", None)
    entry["entry_digest"] = scrubpack_identity.canonical_sha256(
        {key: value for key, value in entry.items() if key != "entry_digest"})
    monkeypatch.setattr(scrubpack_identity, "current_solver_proof_for_candidate",
                        lambda _candidate: (pipeline_bytes, entry))
    monkeypatch.setattr(studio, "list_candidates", lambda: [{"candidate_id": candidate_id}])
    review = {"value": None}
    monkeypatch.setattr(studio, "_latest_review", lambda _candidate: review["value"])
    monkeypatch.setattr(studio, "_latest_ready_pipeline", lambda _candidate: pipeline)

    level = SimpleNamespace(
        level_id="level-1", level_data=SimpleNamespace(payload=level_bytes),
        supply_plan=SimpleNamespace(payload=supply_bytes),
    )
    proof = SimpleNamespace(pipeline_bytes=pipeline_bytes, release_pool_entry=entry)
    assert scrubpack_identity.revalidate_current_solver_proofs([level], {"level-1": proof})

    entry["eligibility_source"] = "OWNER_ACCEPT"
    entry["review_id"] = "review-current"
    entry["entry_digest"] = scrubpack_identity.canonical_sha256(
        {key: value for key, value in entry.items() if key != "entry_digest"})
    review["value"] = {"disposition": "ACCEPT", "review_id": "review-current"}
    assert scrubpack_identity.revalidate_current_solver_proofs([level], {"level-1": proof})

    review["value"] = {"disposition": "ACCEPT", "review_id": "review-stale"}
    with pytest.raises(scrubpack_identity.SolverSupplyIdentityError):
        scrubpack_identity.revalidate_current_solver_proofs([level], {"level-1": proof})

    entry["eligibility_source"] = "READY_AUTO"
    entry["review_id"] = None
    entry["entry_digest"] = scrubpack_identity.canonical_sha256(
        {key: value for key, value in entry.items() if key != "entry_digest"})
    review["value"] = {"disposition": "REJECT", "review_id": "review-rejected"}
    with pytest.raises(scrubpack_identity.SolverSupplyIdentityError):
        scrubpack_identity.revalidate_current_solver_proofs([level], {"level-1": proof})
