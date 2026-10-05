from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CONTENT_PIPELINE = ROOT / "content_pipeline"
sys.path.insert(0, str(CONTENT_PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    ScrubpackLevelInput,
    ScrubpackPayloadInput,
    ScrubpackSolverIdentityError,
    ScrubpackSolverProof,
    build_solver_proven_scrubpack,
    verify_solver_proven_scrubpack,
)
from scrubbots_content_pipeline.scrubpack_builder import ScrubpackBuildError  # noqa: E402
from scrubbots_pixel_factory import owner_upload, studio_extensions as studio  # noqa: E402
from scrubbots_pixel_factory.output.png import encode_logical_png  # noqa: E402
from scrubbots_pixel_factory.supply_pipeline import release_pool  # noqa: E402
from scrubbots_pixel_factory.supply_pipeline.scrubpack_identity import (  # noqa: E402
    current_solver_proof_for_candidate,
    revalidate_current_solver_proofs,
)


EXAMPLES = CONTENT_PIPELINE / "schemas" / "v1" / "examples"


def _json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _descriptor(name: str, level: dict[str, object], plan: dict[str, object], raw: bytes) -> dict[str, object]:
    descriptor = json.loads((EXAMPLES / name).read_text(encoding="utf-8"))
    attributes = descriptor["attributes"]
    attributes["level_id"] = level["id"]
    if name != "supply-plan.json":
        attributes["width"] = level["width"]
        attributes["height"] = level["height"]
    digest_key = "supply_plan_sha256" if name == "supply-plan.json" else "payload_sha256"
    attributes[digest_key] = hashlib.sha256(raw).hexdigest()
    if name == "supply-plan.json":
        attributes["columns"] = plan["columnCount"]
        attributes["preview_depth"] = plan["visiblePreviewDepth"]
    if name == "approved-metadata.json":
        attributes["columns"] = plan["columnCount"]
        attributes["preview_depth"] = plan["visiblePreviewDepth"]
    return descriptor


def _pack_level(level_raw: bytes, plan_raw: bytes) -> ScrubpackLevelInput:
    level = json.loads(level_raw)
    plan = json.loads(plan_raw)
    metadata = {
        "schema": "scrubbots.level.metadata.v1",
        "version": 1,
        "builderVersion": "CPX-001-integration",
        "id": level["id"],
        "width": level["width"],
        "height": level["height"],
        "cellCount": level["width"] * level["height"],
        "difficulty": level["difficulty"],
        "columnCount": plan["columnCount"],
        "visiblePreviewDepth": plan["visiblePreviewDepth"],
        "fileDigests": {
            "level": hashlib.sha256(level_raw).hexdigest(),
            "supply_plan": hashlib.sha256(plan_raw).hexdigest(),
        },
    }
    metadata_raw = _json_bytes(metadata)
    return ScrubpackLevelInput(
        level_id=level["id"],
        level_data=ScrubpackPayloadInput(_descriptor("level.json", level, plan, level_raw), level_raw),
        supply_plan=ScrubpackPayloadInput(_descriptor("supply-plan.json", level, plan, plan_raw), plan_raw),
        metadata=ScrubpackPayloadInput(
            _descriptor("approved-metadata.json", level, plan, metadata_raw), metadata_raw
        ),
    )


def _build_current_authorized_scrubpack(
    levels: tuple[ScrubpackLevelInput, ...],
    *,
    proofs: dict[str, ScrubpackSolverProof],
    pack_id: str,
    pack_version: int = 1,
    created_at_utc: str = "2026-10-05T10:00:00Z",
) -> object:
    return build_solver_proven_scrubpack(
        levels,
        proofs=proofs,
        pack_id=pack_id,
        pack_version=pack_version,
        created_at_utc=created_at_utc,
        current_authority_check=revalidate_current_solver_proofs,
    )


def _release_pool_entry_fixture(
    candidate_id: str,
    review_id: str,
    pipeline: dict[str, object],
    pipeline_bytes: bytes,
    level_bytes: bytes,
    plan_bytes: bytes,
) -> dict[str, object]:
    files = pipeline["primary"]["files"]  # type: ignore[index]
    body: dict[str, object] = {
        "schema": "scrubbots-release-pool-entry/v1",
        "candidate_id": candidate_id,
        "pipeline_run_id": pipeline["run_id"],
        "pipeline_sha256": hashlib.sha256(pipeline_bytes).hexdigest(),
        "pipeline": pipeline,
        "review_id": review_id,
        "files": {
            "level": {"path": files["level"], "sha256": hashlib.sha256(level_bytes).hexdigest()},  # type: ignore[index]
            "supply_plan": {"path": files["supply_plan"], "sha256": hashlib.sha256(plan_bytes).hexdigest()},  # type: ignore[index]
        },
    }
    body["entry_digest"] = hashlib.sha256(_json_bytes(body)).hexdigest()
    return body


def test_real_ready_release_pool_solver_identity_binds_scrubpack_and_rejects_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = tmp_path / "factory-repository"
    source_root = repository / "level_factory/output/owner-uploads"
    evidence_root = repository / "level_factory/output/studio-extensions"
    source_root.mkdir(parents=True)
    evidence_root.mkdir(parents=True)
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda: source_root)
    monkeypatch.setattr(owner_upload, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "owner_upload_root", lambda: source_root)
    monkeypatch.setattr(studio, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "extensions_root", lambda: evidence_root)

    source_path = tmp_path / "current-factory-source.png"
    source_path.write_bytes(encode_logical_png(20, 20, ["C01", "C02", "C03", "C04"] * 100))
    imported = owner_upload.import_owner_upload(source_path)
    source_id = str(imported["source_id"])
    run = studio.run_pipeline(source_id=source_id)
    assert run["disposition"] == "READY"
    assert run["primary"]["state"] == "READY"
    assert run["primary"]["solver_supply_identity"]["solver_state_sha256"]
    candidate_id = str(run["candidate_id"])
    review = studio.record_owner_review(candidate_id, "ACCEPT", "CPX-001 integration proof", "")
    assert review["publication"]["disposition"] == "NOT_ENTERED"
    assert review["publication"]["reason"]

    pipeline_bytes, release_entry = current_solver_proof_for_candidate(candidate_id)
    assert release_entry["schema"] == "scrubbots.factory.accepted-ready-proof/v1"
    assert release_entry not in release_pool.release_entries()
    proof = ScrubpackSolverProof(pipeline_bytes, release_entry)
    level_path = Path(run["primary"]["files"]["level"])
    plan_path = Path(run["primary"]["files"]["supply_plan"])
    level_bytes, plan_bytes = level_path.read_bytes(), plan_path.read_bytes()
    level_input = _pack_level(level_bytes, plan_bytes)
    result = _build_current_authorized_scrubpack(
        (level_input,),
        proofs={level_input.level_id: proof},
        pack_id="cpx001-identity-test",
        pack_version=1,
        created_at_utc="2026-10-05T10:00:00Z",
    )
    artifact = json.loads(result.solver_identity_artifact_bytes)
    binding = artifact["levels"][0]
    assert binding["level_data_sha256"] == hashlib.sha256(level_bytes).hexdigest()
    assert binding["supply_plan_sha256"] == hashlib.sha256(plan_bytes).hexdigest()
    assert binding["fifo_columns"] == json.loads(plan_bytes)["columns"]
    assert binding["column_count"] == json.loads(plan_bytes)["columnCount"]
    assert binding["visible_preview_depth"] == json.loads(plan_bytes)["visiblePreviewDepth"]
    assert binding["max_robots_per_batch"] == json.loads(plan_bytes)["maxRobotsPerBatch"]
    assert binding["source"]["pipeline_sha256"] == hashlib.sha256(pipeline_bytes).hexdigest()
    assert binding["source"]["authority_type"] == "accepted_ready_pipeline"
    assert binding["source"]["release_pool_entry_digest"] is None
    assert verify_solver_proven_scrubpack(
        result.archive_bytes, result.solver_identity_artifact_bytes, result.evidence
    )
    assert not verify_solver_proven_scrubpack(
        result.archive_bytes, result.solver_identity_artifact_bytes + b" ", result.evidence
    )

    def rebuild_with_plan(plan: dict[str, object], *, level_id: str | None = None) -> ScrubpackLevelInput:
        plan_bytes_new = json.dumps(plan, indent="\t", ensure_ascii=False).encode("utf-8")
        level_data = json.loads(level_bytes)
        return _pack_level(level_bytes, plan_bytes_new) if level_id is None else ScrubpackLevelInput(
            level_id,
            _pack_level(level_bytes, plan_bytes_new).level_data,
            _pack_level(level_bytes, plan_bytes_new).supply_plan,
            _pack_level(level_bytes, plan_bytes_new).metadata,
        )

    plan = json.loads(plan_bytes)
    changed_count = json.loads(json.dumps(plan))
    first_batch = next(batch for column in changed_count["columns"] for batch in column)
    first_batch["robots"] += 1
    with pytest.raises(ScrubpackBuildError):
        _build_current_authorized_scrubpack(
            (rebuild_with_plan(changed_count),), proofs={level_input.level_id: proof},
            pack_id="cpx001-drift", pack_version=1, created_at_utc="2026-10-05T10:00:00Z",
        )

    changed_order = json.loads(json.dumps(plan))
    reorderable = next(column for column in changed_order["columns"] if len(column) > 1)
    reorderable[0], reorderable[1] = reorderable[1], reorderable[0]
    with pytest.raises(ScrubpackBuildError):
        _build_current_authorized_scrubpack(
            (rebuild_with_plan(changed_order),), proofs={level_input.level_id: proof},
            pack_id="cpx001-drift", pack_version=1, created_at_utc="2026-10-05T10:00:00Z",
        )

    changed_cid = json.loads(json.dumps(plan))
    changed_cid["columns"][0][0]["cid"] = "C16" if changed_cid["columns"][0][0]["cid"] != "C16" else "C15"
    with pytest.raises(ScrubpackBuildError):
        _build_current_authorized_scrubpack(
            (rebuild_with_plan(changed_cid),), proofs={level_input.level_id: proof},
            pack_id="cpx001-drift", pack_version=1, created_at_utc="2026-10-05T10:00:00Z",
        )

    with pytest.raises(ScrubpackBuildError):
        _build_current_authorized_scrubpack(
            (rebuild_with_plan(plan, level_id=f"{level_input.level_id}-other"),),
            proofs={f"{level_input.level_id}-other": proof}, pack_id="cpx001-drift", pack_version=1,
            created_at_utc="2026-10-05T10:00:00Z",
        )

    whitespace_plan = ScrubpackLevelInput(
        level_input.level_id,
        level_input.level_data,
        ScrubpackPayloadInput(
            _descriptor("supply-plan.json", json.loads(level_bytes), plan, plan_bytes + b" "),
            plan_bytes + b" ",
        ),
        level_input.metadata,
    )
    with pytest.raises(ScrubpackSolverIdentityError):
        _build_current_authorized_scrubpack(
            (whitespace_plan,), proofs={level_input.level_id: proof}, pack_id="cpx001-drift",
            pack_version=1, created_at_utc="2026-10-05T10:00:00Z",
        )

    changed_state = json.loads(pipeline_bytes)
    changed_state["primary"]["solver_supply_identity"]["solver_state_sha256"] = "0" * 64
    changed_state["primary"]["result"]["solver_supply_identity"]["solver_state_sha256"] = "0" * 64
    changed_pipeline_proof = ScrubpackSolverProof(_json_bytes(changed_state), release_entry)
    with pytest.raises(ScrubpackSolverIdentityError):
        _build_current_authorized_scrubpack(
            (level_input,), proofs={level_input.level_id: changed_pipeline_proof}, pack_id="cpx001-drift",
            pack_version=1, created_at_utc="2026-10-05T10:00:00Z",
        )

    changed_evidence = json.loads(pipeline_bytes)
    changed_evidence["primary"]["solver_supply_identity"]["solver_evidence_sha256"] = "f" * 64
    changed_evidence["primary"]["result"]["solver_supply_identity"]["solver_evidence_sha256"] = "f" * 64
    changed_evidence_proof = ScrubpackSolverProof(_json_bytes(changed_evidence), release_entry)
    with pytest.raises(ScrubpackSolverIdentityError):
        _build_current_authorized_scrubpack(
            (level_input,), proofs={level_input.level_id: changed_evidence_proof}, pack_id="cpx001-drift",
            pack_version=1, created_at_utc="2026-10-05T10:00:00Z",
        )

    stale_review = dict(release_entry)
    stale_review["candidate_id"] = "another-candidate"
    with pytest.raises(ScrubpackSolverIdentityError):
        _build_current_authorized_scrubpack(
            (level_input,), proofs={level_input.level_id: ScrubpackSolverProof(pipeline_bytes, stale_review)},
            pack_id="cpx001-drift", pack_version=1, created_at_utc="2026-10-05T10:00:00Z",
        )

    studio.record_owner_review(candidate_id, "REJECT", "stale proof check", "")
    stale_reject_result = None
    with pytest.raises(ValueError, match="no current owner-accepted READY pipeline"):
        stale_reject_result = _build_current_authorized_scrubpack(
            (level_input,), proofs={level_input.level_id: proof}, pack_id="cpx001-race-reject"
        )
    assert stale_reject_result is None
    with pytest.raises(ValueError, match="no current owner-accepted READY pipeline"):
        current_solver_proof_for_candidate(candidate_id)

    review_a = studio.record_owner_review(candidate_id, "ACCEPT", "race B accept A", "")
    pipeline_a_bytes, proof_a_source = current_solver_proof_for_candidate(candidate_id)
    proof_a = ScrubpackSolverProof(pipeline_a_bytes, proof_a_source)
    review_b = studio.record_owner_review(candidate_id, "ACCEPT", "race B accept B", "")
    assert review_a["review_id"] != review_b["review_id"]
    stale_accept_result = None
    with pytest.raises(ValueError, match="proof changed"):
        stale_accept_result = _build_current_authorized_scrubpack(
            (level_input,), proofs={level_input.level_id: proof_a}, pack_id="cpx001-race-accept"
        )
    assert stale_accept_result is None

    _, proof_b_source = current_solver_proof_for_candidate(candidate_id)
    pipeline_b_bytes, _ = current_solver_proof_for_candidate(candidate_id)
    proof_b = ScrubpackSolverProof(pipeline_b_bytes, proof_b_source)
    ready_b = studio.run_pipeline(source_id=source_id)
    assert ready_b["disposition"] == "READY"
    assert ready_b["run_id"] != proof_b_source["pipeline_run_id"]
    stale_ready_result = None
    with pytest.raises(ValueError, match="proof changed"):
        stale_ready_result = _build_current_authorized_scrubpack(
            (level_input,), proofs={level_input.level_id: proof_b}, pack_id="cpx001-race-ready"
        )
    assert stale_ready_result is None

    # Release Pool authority uses a real current READY pipeline and owner review,
    # with only its projection admitted by this focused fixture.
    current_pipeline_bytes, _ = current_solver_proof_for_candidate(candidate_id)
    current_pipeline = json.loads(current_pipeline_bytes)
    current_level_bytes = Path(current_pipeline["primary"]["files"]["level"]).read_bytes()
    current_plan_bytes = Path(current_pipeline["primary"]["files"]["supply_plan"]).read_bytes()
    current_level_input = _pack_level(current_level_bytes, current_plan_bytes)
    pool_entry = _release_pool_entry_fixture(
        candidate_id,
        str(review_b["review_id"]),
        current_pipeline,
        current_pipeline_bytes,
        current_level_bytes,
        current_plan_bytes,
    )
    projection = [pool_entry]
    monkeypatch.setattr(release_pool, "release_entries", lambda: list(projection))
    pool_pipeline_bytes, pool_source = current_solver_proof_for_candidate(candidate_id)
    assert pool_source["schema"] == "scrubbots-release-pool-entry/v1"
    pool_proof = ScrubpackSolverProof(pool_pipeline_bytes, pool_source)
    pool_result = _build_current_authorized_scrubpack(
        (current_level_input,),
        proofs={current_level_input.level_id: pool_proof},
        pack_id="cpx001-current-pool-control",
    )
    assert pool_result.archive_bytes
    projection.clear()
    stale_pool_result = None
    with pytest.raises(ValueError, match="proof changed"):
        stale_pool_result = _build_current_authorized_scrubpack(
            (current_level_input,),
            proofs={current_level_input.level_id: pool_proof},
            pack_id="cpx001-race-pool-revoked",
        )
    assert stale_pool_result is None
    projection.append(pool_entry)
    studio.record_owner_review(candidate_id, "REJECT", "revoke current Release Pool owner authority", "")
    stale_pool_review_result = None
    with pytest.raises(ValueError, match="current owner review or READY pipeline identity changed"):
        stale_pool_review_result = _build_current_authorized_scrubpack(
            (current_level_input,),
            proofs={current_level_input.level_id: pool_proof},
            pack_id="cpx001-race-pool-review-revoked",
        )
    assert stale_pool_review_result is None
