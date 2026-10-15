from __future__ import annotations

import hashlib

import pytest

from scrubbots_pixel_factory.contracts.candidate_provenance import (
    CandidateClass,
    CandidateProvenanceError,
    validate_candidate_classification,
)
from scrubbots_pixel_factory.core import DeterministicRNG, GenerationRequest, GenerationResult, RNG_ALGORITHM
from scrubbots_pixel_factory.output.bundle import build_export_bundle
from scrubbots_pixel_factory.output.png import encode_logical_png
from scrubbots_pixel_factory.quality import evaluate_grid
from scrubbots_pixel_factory.supply_pipeline import release_pool
from scrubbots_pixel_factory.supply_pipeline.release_pool import ReleaseError, enter_release_pool, validate_pool_candidate_provenance


def _candidate(
    *, owner_source: bool, source_cells: tuple[str, ...] | None = None, candidate_cells: tuple[str, ...] | None = None
) -> dict[str, object]:
    cells = candidate_cells or tuple(("C01", "C02", "C03")[index % 3] for index in range(400))
    source_cells = source_cells or cells
    source_png = encode_logical_png(20, 20, source_cells) if owner_source else b""
    source_sha = hashlib.sha256(source_png if owner_source else b"test-seed").hexdigest()
    request = GenerationRequest(seed=source_sha, width=20, height=20)
    candidate_id = f"candidate-owner-{source_sha[:48]}" if owner_source else "candidate-fixture"
    rng = DeterministicRNG(request.seed)
    result = GenerationResult.success(
        request=request,
        width=20,
        height=20,
        logical_grid=cells,
        generator_id="owner-upload-canonical-derive" if owner_source else "provenance-fixture",
        generator_version="1" if owner_source else "1.0.0",
        rng_algorithm=RNG_ALGORITHM,
        provenance={"stage_seeds": rng.stage_seeds()},
    )
    metadata = None
    if owner_source:
        metadata = {
            "namespace": "owner-upload",
            "data": {
                "source_lineage": {
                    "source_id": f"owner-upload-{source_sha}",
                    "source_sha256": source_sha,
                    "source_record": f"level_factory/output/owner-uploads/owner-upload-{source_sha}/source.json",
                    "source_bytes_unchanged": True,
                    "derivation": "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE",
                }
            },
        }
    bundle = build_export_bundle(
        result,
        candidate_id,
        quality_report=evaluate_grid(20, 20, cells),
        generator_metadata=metadata,
    )
    return {
        "candidate_id": bundle.artwork.candidate_id,
        "artwork_sha256": hashlib.sha256(bundle.artwork_png).hexdigest(),
        "grid_hash": bundle.artwork.grid_hash,
        "metadata": bundle.metadata,
        "source_path": f"level_factory/output/studio-derived-candidates/{candidate_id}",
        "source_png": source_png,
        "artwork_png": bundle.artwork_png,
    }


def _source_record(candidate: dict[str, object], source_png: bytes) -> dict[str, object]:
    metadata = candidate["metadata"]
    classification = metadata["generator_metadata"]["classification"]
    source_id = f"owner-upload-{classification['source_sha256']}"
    return {
        "source_id": source_id,
        "source_sha256": classification["source_sha256"],
        "source_bytes_sha256": hashlib.sha256(source_png).hexdigest(),
        "origin": "OWNER_UPLOAD",
        "status": "SOURCE_ONLY",
        "validation_state": "UNVALIDATED",
        "original_width": 20,
        "original_height": 20,
    }


def _owner_accept(candidate: dict[str, object]) -> dict[str, object]:
    return {
        "disposition": "ACCEPT",
        "review_id": "review-current",
        "candidate_id": candidate["candidate_id"],
        "artwork_sha256": candidate["artwork_sha256"],
    }


def test_generated_candidate_defaults_to_test_and_is_request_bound() -> None:
    candidate = _candidate(owner_source=False)
    metadata = candidate["metadata"]
    assert isinstance(metadata, dict)
    generator = metadata["generator_metadata"]
    classification = generator["classification"]
    assert classification["candidate_class"] == CandidateClass.TEST.value
    assert classification["candidate_id"] == candidate["candidate_id"]
    assert classification["request_sha256"]
    assert classification["generator_version"] == "1.0.0"
    assert classification["attempt_id"].startswith("candidate-fixture:attempt:")

    forged = {**classification, "candidate_class": CandidateClass.PRODUCTION_CANDIDATE.value}
    with pytest.raises(CandidateProvenanceError):
        validate_candidate_classification(
            forged,
            metadata["generation"]["result"],
            candidate_id=candidate["candidate_id"],
            grid_hash=candidate["grid_hash"],
            generator_metadata=generator["payload"],
        )
    with pytest.raises(ReleaseError, match="TEST candidate"):
        validate_pool_candidate_provenance(candidate, None)
    with pytest.raises(ReleaseError, match="TEST candidate"):
        enter_release_pool(
            candidate,
            {"disposition": "READY", "primary": {"state": "READY"}},
            {"disposition": "ACCEPT", "candidate_id": candidate["candidate_id"], "artwork_sha256": candidate["artwork_sha256"]},
        )


@pytest.mark.parametrize(
    "candidate_class",
    [
        CandidateClass.TEST,
        CandidateClass.DEVELOPMENT,
        CandidateClass.PREVIEW,
        CandidateClass.UNAVAILABLE,
        CandidateClass.PRODUCTION_CANDIDATE,
    ],
)
def test_non_owner_candidate_classes_fail_actual_pool_promotion(candidate_class: CandidateClass) -> None:
    candidate = _candidate(owner_source=False)
    metadata = candidate["metadata"]
    metadata["generator_metadata"]["classification"]["candidate_class"] = candidate_class.value
    review = _owner_accept(candidate)
    pipeline = {"disposition": "READY", "primary": {"state": "READY"}}
    with pytest.raises(ReleaseError):
        validate_pool_candidate_provenance(candidate, review)
    with pytest.raises(ReleaseError):
        enter_release_pool(candidate, pipeline, review)


def test_owner_source_requires_exact_current_owner_accept_at_pool_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    candidate = _candidate(owner_source=True)
    source_png = candidate["source_png"]
    monkeypatch.setattr(
        release_pool,
        "_verify_candidate_source_grid_binding",
        lambda item, classification: release_pool._validate_source_grid_bytes(
            item, classification, item["metadata"]["generator_metadata"]["payload"]["data"]["source_lineage"],
            _source_record(item, source_png), source_png, item["artwork_png"]
        ),
    )
    classification = validate_pool_candidate_provenance(
        candidate,
        _owner_accept(candidate),
    )
    assert classification["candidate_class"] == CandidateClass.PRODUCTION_CANDIDATE.value
    assert classification["source_sha256"]

    with pytest.raises(ReleaseError, match="exact current owner ACCEPT"):
        validate_pool_candidate_provenance(candidate, None)
    with pytest.raises(ReleaseError, match="exact current owner ACCEPT"):
        validate_pool_candidate_provenance(
            candidate,
            {"disposition": "ACCEPT", "candidate_id": "other", "artwork_sha256": candidate["artwork_sha256"]},
        )
    metadata = candidate["metadata"]
    generator = metadata["generator_metadata"]
    forged_classification = {**generator["classification"], "source_sha256": "0" * 64}
    with pytest.raises(CandidateProvenanceError, match="does not match request"):
        validate_candidate_classification(
            forged_classification,
            metadata["generation"]["result"],
            candidate_id=candidate["candidate_id"],
            grid_hash=candidate["grid_hash"],
            generator_metadata=generator["payload"],
        )

    # The claimed source identity and its PNG digest are genuine, but its
    # decoded cell grid differs from the selected candidate's artwork.
    mismatched_cells = tuple(("C04", "C05", "C06")[index % 3] for index in range(400))
    forged = _candidate(owner_source=True, source_cells=mismatched_cells, candidate_cells=tuple(("C01", "C02", "C03")[index % 3] for index in range(400)))
    mismatched_source = forged["source_png"]
    monkeypatch.setattr(
        release_pool,
        "_verify_candidate_source_grid_binding",
        lambda item, classification: release_pool._validate_source_grid_bytes(
            item, classification, item["metadata"]["generator_metadata"]["payload"]["data"]["source_lineage"],
            _source_record(item, mismatched_source), mismatched_source, item["artwork_png"]
        ),
    )
    with pytest.raises(ReleaseError, match="does not equal the exact OWNER_UPLOAD-derived grid"):
        validate_pool_candidate_provenance(forged, _owner_accept(forged))


def _release_entry(candidate_id: str, *, production: bool) -> dict[str, object]:
    return {
        "candidate_id": candidate_id,
        "candidate_classification": (
            {"candidate_class": CandidateClass.PRODUCTION_CANDIDATE.value} if production else None
        ),
        "eligibility_source": "OWNER_ACCEPT" if production else "READY_AUTO",
        "review_id": "review-current" if production else None,
        "candidate": {"candidate_id": candidate_id},
        "pipeline": {"disposition": "READY"},
    }


def test_legacy_ready_auto_is_visible_but_cannot_enter_plan_or_approval(monkeypatch: pytest.MonkeyPatch) -> None:
    from pathlib import Path

    from scrubbots_pixel_factory import studio_extensions as studio

    legacy = _release_entry("legacy-ready-auto", production=False)
    accepted = _release_entry("owner-accepted", production=True)
    monkeypatch.setattr(release_pool, "release_entries", lambda: [legacy, accepted])
    monkeypatch.setattr(
        studio,
        "_latest_review",
        lambda candidate_id: _owner_accept({"candidate_id": candidate_id, "artwork_sha256": "art"})
        if candidate_id == "owner-accepted" else None,
    )
    monkeypatch.setattr(release_pool, "discover_game_project", lambda _game: Path("synthetic-game"))
    monkeypatch.setattr(release_pool, "_game_authority", lambda _game: ({}, {}))
    planned: dict[str, object] = {}

    def build_campaign_plan(**kwargs: object) -> dict[str, object]:
        planned["pool"] = kwargs["pool"]
        return {"plan_hash": "synthetic-plan", "slots": []}

    monkeypatch.setattr(release_pool, "build_campaign_plan", build_campaign_plan)
    monkeypatch.setattr(release_pool, "write_campaign_plan", lambda *_args: None)
    monkeypatch.setattr(studio, "extensions_root", lambda: Path("synthetic-extensions"))
    release_pool.build_release_plan(game_project="synthetic-game")
    assert [entry["candidate_id"] for entry in planned["pool"]] == ["owner-accepted"]

    legacy_plan = {"plan_hash": "legacy-plan", "K": 1, "slots": [{"n": 1, "chosen_id": "legacy-ready-auto"}]}
    monkeypatch.setattr(release_pool, "release_entries", lambda: [legacy])
    monkeypatch.setattr(release_pool, "_json", lambda _path: legacy_plan)
    with pytest.raises(ReleaseError, match="legacy or no-longer-eligible"):
        release_pool.validate_release_plan(plan_hash="legacy-plan", game_project="synthetic-game")
    publish_calls: list[object] = []
    monkeypatch.setattr(release_pool, "publish_batch", lambda **kwargs: publish_calls.append(kwargs))
    with pytest.raises(ReleaseError, match="legacy or no-longer-eligible"):
        release_pool.approve_release_plan(plan_hash="legacy-plan", game_project="synthetic-game")
    assert publish_calls == []


@pytest.mark.parametrize(
    "candidate_class",
    [CandidateClass.TEST, CandidateClass.DEVELOPMENT, CandidateClass.PREVIEW, CandidateClass.UNAVAILABLE],
)
def test_nonproduction_class_cannot_be_selected_for_approval(
    candidate_class: CandidateClass, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pathlib import Path

    from scrubbots_pixel_factory import studio_extensions as studio

    entry = _release_entry("not-production", production=True)
    entry["candidate_classification"] = {"candidate_class": candidate_class.value}
    plan = {"plan_hash": "nonproduction-plan", "K": 1, "slots": [{"n": 1, "chosen_id": "not-production"}]}
    monkeypatch.setattr(release_pool, "release_entries", lambda: [entry])
    monkeypatch.setattr(studio, "_latest_review", lambda _candidate_id: {"disposition": "ACCEPT", "review_id": "review-current"})
    monkeypatch.setattr(studio, "extensions_root", lambda: Path("synthetic-extensions"))
    monkeypatch.setattr(release_pool, "discover_game_project", lambda _game: Path("synthetic-game"))
    monkeypatch.setattr(release_pool, "_json", lambda _path: plan)
    publish_calls: list[object] = []
    monkeypatch.setattr(release_pool, "publish_batch", lambda **kwargs: publish_calls.append(kwargs))
    with pytest.raises(ReleaseError, match="legacy or no-longer-eligible"):
        release_pool.approve_release_plan(plan_hash="nonproduction-plan", game_project="synthetic-game")
    assert publish_calls == []
