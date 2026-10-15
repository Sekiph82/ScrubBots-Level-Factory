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
from scrubbots_pixel_factory.quality import evaluate_grid
from scrubbots_pixel_factory.supply_pipeline.release_pool import ReleaseError, enter_release_pool, validate_pool_candidate_provenance


def _candidate(*, owner_source: bool) -> dict[str, object]:
    source_sha = hashlib.sha256(b"owner-source-bytes" if owner_source else b"test-seed").hexdigest()
    request = GenerationRequest(seed=source_sha, width=20, height=20)
    candidate_id = f"candidate-owner-{source_sha[:48]}" if owner_source else "candidate-fixture"
    rng = DeterministicRNG(request.seed)
    cells = tuple(("C01", "C02", "C03")[index % 3] for index in range(400))
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


def test_owner_source_requires_exact_current_owner_accept_at_pool_boundary() -> None:
    candidate = _candidate(owner_source=True)
    classification = validate_pool_candidate_provenance(
        candidate,
        {
            "disposition": "ACCEPT",
            "candidate_id": candidate["candidate_id"],
            "artwork_sha256": candidate["artwork_sha256"],
        },
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
    forged = {**generator["classification"], "source_sha256": "0" * 64}
    with pytest.raises(CandidateProvenanceError, match="does not match request"):
        validate_candidate_classification(
            forged,
            metadata["generation"]["result"],
            candidate_id=candidate["candidate_id"],
            grid_hash=candidate["grid_hash"],
            generator_metadata=generator["payload"],
        )
