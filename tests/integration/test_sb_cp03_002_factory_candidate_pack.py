from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CONTENT_PIPELINE = ROOT / "content_pipeline"
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(CONTENT_PIPELINE / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from scrubbots_content_pipeline import verify_solver_proven_scrubpack  # noqa: E402
from scrubbots_pixel_factory import owner_upload, studio_extensions as studio  # noqa: E402
from scrubbots_pixel_factory.output.png import encode_logical_png  # noqa: E402
from scrubbots_pixel_factory.supply_pipeline import scrubpack_identity  # noqa: E402
import build_accepted_factory_output_pack as candidate_pack_module  # noqa: E402
from build_accepted_factory_output_pack import (  # noqa: E402
    FactoryPackAssemblyError,
    build_accepted_factory_output_pack,
)
from scrubbots_pixel_factory.supply_pipeline import release_pool  # noqa: E402


@pytest.fixture
def accepted_factory_candidate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[str, dict[str, object]]:
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

    source_path = tmp_path / "accepted-factory-source.png"
    source_path.write_bytes(encode_logical_png(20, 20, ["C01", "C02", "C03", "C04"] * 100))
    imported = owner_upload.import_owner_upload(source_path)
    run = studio.run_pipeline(source_id=str(imported["source_id"]))
    assert run["disposition"] == "READY"
    assert run["primary"]["state"] == "READY"
    review = studio.record_owner_review(str(run["candidate_id"]), "ACCEPT", "CP03-002 current pack test", "")
    assert review["disposition"] == "ACCEPT"
    return str(run["candidate_id"]), review


def test_explicit_current_accept_membership_builds_deterministic_solver_pack(
    accepted_factory_candidate: tuple[str, dict[str, object]], monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate_id, review = accepted_factory_candidate
    calls: list[tuple[int, int]] = []
    original_revalidate = scrubpack_identity.revalidate_current_solver_proofs

    def observe_final_revalidation(levels, proofs):
        calls.append((len(levels), len(proofs)))
        return original_revalidate(levels, proofs)

    monkeypatch.setattr(candidate_pack_module, "revalidate_current_solver_proofs", observe_final_revalidation)
    kwargs = {
        "pack_id": "m14-current-factory",
        "pack_version": 1,
        "created_at_utc": "2026-10-06T14:00:00Z",
    }
    first = build_accepted_factory_output_pack((candidate_id,), **kwargs)
    second = build_accepted_factory_output_pack((candidate_id,), **kwargs)

    assert first.archive_bytes == second.archive_bytes
    assert first.evidence == second.evidence
    assert first.evidence.pack_id == "m14-current-factory"
    assert first.evidence.pack_version == 1
    assert first.evidence.created_at_utc == "2026-10-06T14:00:00Z"
    assert first.evidence.level_count == 1
    assert len(first.evidence.level_ids) == 1
    assert first.solver_identity_artifact_bytes is not None
    assert verify_solver_proven_scrubpack(
        first.archive_bytes, first.solver_identity_artifact_bytes, first.evidence
    )
    assert calls == [(1, 1), (1, 1)]
    assert studio._latest_review(candidate_id)["review_id"] == review["review_id"]


def test_requires_explicit_nonduplicated_membership_and_current_acceptance(
    accepted_factory_candidate: tuple[str, dict[str, object]]
) -> None:
    candidate_id, _ = accepted_factory_candidate
    with pytest.raises(FactoryPackAssemblyError, match="duplicated"):
        build_accepted_factory_output_pack(
            (candidate_id, candidate_id), pack_id="dup", pack_version=1,
            created_at_utc="2026-10-06T14:00:00Z",
        )

    studio.record_owner_review(candidate_id, "REJECT", "revoke current pack authority", "")
    with pytest.raises(FactoryPackAssemblyError, match="current owner-accepted READY"):
        build_accepted_factory_output_pack(
            (candidate_id,), pack_id="stale", pack_version=1,
            created_at_utc="2026-10-06T14:00:00Z",
        )


def test_rejects_malformed_explicit_membership_before_factory_reads() -> None:
    with pytest.raises(FactoryPackAssemblyError, match="explicit sequence"):
        build_accepted_factory_output_pack(
            "candidate-1", pack_id="invalid", pack_version=1,
            created_at_utc="2026-10-06T14:00:00Z",
        )

    with pytest.raises(FactoryPackAssemblyError, match="empty, malformed, or duplicated"):
        build_accepted_factory_output_pack(
            ("../candidate-1",), pack_id="invalid", pack_version=1,
            created_at_utc="2026-10-06T14:00:00Z",
        )


def test_rejects_pipeline_source_path_outside_factory_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository = tmp_path / "factory-root"
    repository.mkdir()
    outside = tmp_path / "untrusted-level.json"
    outside.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(studio, "_repository_root", lambda: repository)
    pipeline = {
        "schema": "scrubbots-studio-pipeline-run",
        "version": 2,
        "disposition": "READY",
        "candidate_id": "candidate-1",
        "run_id": "run-1",
        "primary": {
            "state": "READY",
            "disposition": "READY",
            "files": {"level": str(outside), "supply_plan": str(outside)},
        },
    }
    source = {"candidate_id": "candidate-1", "pipeline_run_id": "run-1"}
    monkeypatch.setattr(
        candidate_pack_module, "current_solver_proof_for_candidate",
        lambda candidate_id: (json.dumps(pipeline).encode("utf-8"), source),
    )

    with pytest.raises(FactoryPackAssemblyError, match="escaped the Factory repository"):
        build_accepted_factory_output_pack(
            ("candidate-1",), pack_id="untrusted-path", pack_version=1,
            created_at_utc="2026-10-06T14:00:00Z",
        )


def test_current_release_pool_projection_is_an_accepted_pack_source(
    accepted_factory_candidate: tuple[str, dict[str, object]], monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate_id, review = accepted_factory_candidate
    pipeline_bytes, _ = scrubpack_identity.current_solver_proof_for_candidate(candidate_id)
    pipeline = json.loads(pipeline_bytes)
    files = pipeline["primary"]["files"]
    level_path, plan_path = Path(files["level"]), Path(files["supply_plan"])
    body: dict[str, object] = {
        "schema": "scrubbots-release-pool-entry/v1",
        "candidate_id": candidate_id,
        "pipeline_run_id": pipeline["run_id"],
        "pipeline_sha256": hashlib.sha256(pipeline_bytes).hexdigest(),
        "pipeline": pipeline,
        "review_id": review["review_id"],
        "files": {
            "level": {"path": str(level_path), "sha256": hashlib.sha256(level_path.read_bytes()).hexdigest()},
            "supply_plan": {"path": str(plan_path), "sha256": hashlib.sha256(plan_path.read_bytes()).hexdigest()},
        },
    }
    canonical = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    body["entry_digest"] = hashlib.sha256(canonical).hexdigest()
    monkeypatch.setattr(release_pool, "release_entries", lambda: [body])

    result = build_accepted_factory_output_pack(
        (candidate_id,), pack_id="m14-release-pool", pack_version=2,
        created_at_utc="2026-10-06T14:00:00Z",
    )

    artifact = json.loads(result.solver_identity_artifact_bytes)
    assert artifact["levels"][0]["source"]["authority_type"] == "release_pool"
    assert artifact["levels"][0]["source"]["release_pool_entry_digest"] == body["entry_digest"]
    assert verify_solver_proven_scrubpack(
        result.archive_bytes, result.solver_identity_artifact_bytes, result.evidence
    )
