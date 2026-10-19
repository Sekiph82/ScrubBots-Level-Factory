"""Owner Release Pool, campaign plan, lock validation, and batch approval."""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ..contracts.candidate_provenance import CandidateClass, CandidateProvenanceError, validate_verified_owner_upload_classification
from .campaign_builder import CampaignError, build_campaign_plan, write_campaign_plan
from .game_publisher import PublicationError, discover_game_project, publish_batch
from .progression import load_progression_authority


class ReleaseError(ValueError):
    pass


_DIFFICULTY_PROFILES = {"FLOW", "COLOR", "FORTRESS", "ROUTE", "MARATHON", "BALANCED"}


def validate_pool_candidate_provenance(
    candidate: Mapping[str, Any], review: Mapping[str, Any] | None
) -> dict[str, Any]:
    """Require verified owner-source provenance; ACCEPT is optional for pool eligibility."""

    metadata = candidate.get("metadata")
    if not isinstance(metadata, Mapping):
        raise ReleaseError("candidate has no verifiable bundle metadata; production classification is unavailable")
    generation = metadata.get("generation")
    generation = generation if isinstance(generation, Mapping) else {}
    result = generation.get("result")
    result = result if isinstance(result, Mapping) else {}
    generator_metadata = metadata.get("generator_metadata")
    generator_metadata = generator_metadata if isinstance(generator_metadata, Mapping) else {}
    payload = generator_metadata.get("payload")
    payload = payload if isinstance(payload, Mapping) else {}
    classification = generator_metadata.get("classification")
    if not isinstance(classification, Mapping):
        raise ReleaseError("candidate has no verified owner-upload classification")
    claimed_class = classification.get("candidate_class")
    if type(claimed_class) is not str:
        raise ReleaseError("candidate has no valid production candidate class")
    try:
        claimed_class = CandidateClass(claimed_class)
    except ValueError:
        raise ReleaseError("candidate has an invalid production candidate class") from None
    if claimed_class is not CandidateClass.PRODUCTION_CANDIDATE:
        raise ReleaseError(f"{claimed_class.value} candidate cannot enter the production Release Pool")
    try:
        verified_source_sha256 = _verify_candidate_source_grid_binding(candidate, classification)
        candidate_class = validate_verified_owner_upload_classification(
            classification,
            result,
            candidate_id=str(candidate.get("candidate_id", "")),
            grid_hash=str(candidate.get("grid_hash", "")),
            generator_metadata=payload,
            verified_source_sha256=verified_source_sha256,
        )
    except CandidateProvenanceError as exc:
        raise ReleaseError(str(exc)) from exc
    if candidate_class is not CandidateClass.PRODUCTION_CANDIDATE:
        raise ReleaseError(f"{candidate_class.value} candidate cannot enter the production Release Pool")
    data = payload.get("data")
    data = data if isinstance(data, Mapping) else {}
    lineage = data.get("source_lineage")
    if (payload.get("namespace") != "owner-upload" or not isinstance(lineage, Mapping)
            or lineage.get("source_sha256") != generator_metadata["classification"].get("source_sha256")
            or lineage.get("source_bytes_unchanged") is not True
            or lineage.get("derivation") != "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE"):
        raise ReleaseError("production candidate is not bound to unchanged canonical OWNER_UPLOAD source bytes")
    if review is not None and (
        not isinstance(review, Mapping) or review.get("disposition") != "ACCEPT"
        or review.get("candidate_id") != candidate.get("candidate_id")
        or review.get("artwork_sha256") != candidate.get("artwork_sha256")
    ):
        raise ReleaseError("pool restoration requires an exact current owner ACCEPT review")
    return dict(classification)


def inspect_current_game_candidate_provenance(
    candidate: Mapping[str, Any],
    review: Mapping[str, Any] | None,
    ready_evidence: Mapping[str, Any] | None,
    static_preflight: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Read-only, selected-candidate lineage summary for current-game readiness.

    Reuses the Release Pool's authoritative owner-source/grid/review validator.
    It never inserts into the pool or starts a solver, replay, or pipeline job.
    """
    metadata = candidate.get("metadata")
    generator = metadata.get("generator_metadata") if isinstance(metadata, Mapping) else None
    classification = generator.get("classification") if isinstance(generator, Mapping) else None
    if not isinstance(classification, Mapping):
        return {"disposition": "OWNER_PROVENANCE_UNAVAILABLE", "compatible": False,
                "reason_codes": ["VERIFIED_OWNER_UPLOAD_CLASSIFICATION_REQUIRED"],
                "runtime_executed": False, "release_pool_mutated": False}
    try:
        verified = validate_pool_candidate_provenance(candidate, review)
        source_id = str(_candidate_source_lineage(candidate).get("source_id", ""))
        from .. import studio_extensions as studio
        record_path, _source_path = studio._source_record_paths(source_id)
        repository = studio._repository_root().resolve()
        if (not record_path.resolve().is_relative_to(repository) or record_path.is_symlink()
                or record_path.stat().st_size > 64 * 1024):
            raise ReleaseError("OWNER_UPLOAD source record path or size is invalid")
        record_sha = hashlib.sha256(record_path.read_bytes()).hexdigest()
        ready_primary = ready_evidence.get("primary", {}) if isinstance(ready_evidence, Mapping) else {}
        lineage = _candidate_source_lineage(candidate)
        owner_binding = ready_evidence.get("owner_source_binding", {}) if isinstance(ready_evidence, Mapping) else {}
        expected_record_digests = [
            verified.get("source_record_sha256"), lineage.get("source_record_sha256"),
            owner_binding.get("source_record_sha256") if isinstance(owner_binding, Mapping) else None,
            ready_primary.get("source_record_sha256") if isinstance(ready_primary, Mapping) else None,
        ]
        expected_record_digests = [value for value in expected_record_digests if value is not None]
        if not expected_record_digests or any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value)
                                              for value in expected_record_digests):
            raise ReleaseError("SOURCE_RECORD_DIGEST_AUTHORITY_MISSING")
        if any(expected != record_sha for expected in expected_record_digests):
            raise ReleaseError("OWNER_UPLOAD source record SHA-256 does not match candidate provenance")
    except (ReleaseError, OSError, TypeError, ValueError) as exc:
        return {"disposition": "OWNER_PROVENANCE_REJECTED", "compatible": False,
                "reason_codes": (["SOURCE_RECORD_DIGEST_AUTHORITY_MISSING"] if "SOURCE_RECORD_DIGEST_AUTHORITY_MISSING" in str(exc)
                                 else [f"OWNER_PROVENANCE_INVALID:{str(exc)[:180]}"]),
                "runtime_executed": False, "release_pool_mutated": False}
    primary = ready_evidence.get("primary", {}) if isinstance(ready_evidence, Mapping) else {}
    load_check = primary.get("load_check", {}) if isinstance(primary, Mapping) else {}
    ready = (isinstance(ready_evidence, Mapping) and ready_evidence.get("disposition") == "READY"
             and isinstance(primary, Mapping) and primary.get("state") == "READY"
             and isinstance(load_check, Mapping) and load_check.get("state") == "READY"
             and load_check.get("disposition") == "READY")
    static_ok = (isinstance(static_preflight, Mapping)
                 and static_preflight.get("compatible") is True
                 and static_preflight.get("candidate_id") == candidate.get("candidate_id")
                 and static_preflight.get("logical_grid_hash") == candidate.get("grid_hash"))
    if not ready or not static_ok:
        reasons = []
        if not ready:
            reasons.append("CURRENT_READY_AND_LOAD_CHECK_EVIDENCE_REQUIRED")
        if not static_ok:
            reasons.append("CURRENT_GAME_STATIC_PREFLIGHT_MUST_MATCH_SELECTED_CANDIDATE_GRID")
        return {"disposition": "OWNER_PROVENANCE_VERIFIED_CURRENT_GAME_NOT_READY", "compatible": False,
                "candidate_class": verified.get("candidate_class"),
                "source_sha256": verified.get("source_sha256"), "source_record_sha256": record_sha,
                "review_id": review.get("review_id") if isinstance(review, Mapping) else None,
                "reason_codes": reasons, "runtime_executed": False, "release_pool_mutated": False}
    return {"disposition": "OWNER_PROVENANCE_VERIFIED_STATIC_ONLY", "compatible": True,
            "candidate_class": verified.get("candidate_class"),
            "source_sha256": verified.get("source_sha256"), "source_record_sha256": record_sha,
            "review_id": review.get("review_id") if isinstance(review, Mapping) else None,
            "historical_cohort_status": "SAVED_HISTORICAL_UNVERIFIED",
            "reason_codes": ["OWNER_SOURCE_GRID_REVIEW_READY_LOAD_CHECK_AND_FIFO_STATIC_EVIDENCE_MATCHED",
                             "CURRENT_MAIN_RUNTIME_NOT_EXECUTED"],
            "runtime_executed": False, "release_pool_mutated": False}


def _validate_source_grid_bytes(
    candidate: Mapping[str, Any],
    classification: Mapping[str, Any],
    lineage: Mapping[str, Any],
    source_record: Mapping[str, Any],
    source_png: bytes,
    candidate_png: bytes,
) -> None:
    """Prove one selected candidate's logical cells equal its exact OWNER_UPLOAD PNG."""

    from ..output.png import PNGContractError, decode_logical_png
    from ..quality.core import logical_grid_hash
    from .. import studio_extensions as studio

    source_id = lineage.get("source_id")
    source_sha256 = lineage.get("source_sha256")
    if (lineage.get("derivation") != "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE"
            or lineage.get("source_bytes_unchanged") is not True
            or type(source_id) is not str or source_record.get("source_id") != source_id
            or source_record.get("origin") != "OWNER_UPLOAD"
            or source_record.get("status") != "SOURCE_ONLY"
            or source_record.get("validation_state") != "UNVALIDATED"
            or source_sha256 != classification.get("source_sha256")
            or source_record.get("source_sha256") != source_sha256
            or source_record.get("source_bytes_sha256") != source_sha256
            or hashlib.sha256(source_png).hexdigest() != source_sha256):
        raise ReleaseError("candidate source lineage does not match the exact immutable OWNER_UPLOAD bytes")
    try:
        source_width, source_height, source_cells, foreign, semi_alpha, _transparent, _used = (
            studio._owner_source_grid(source_png)
        )
    except (PNGContractError, TypeError, ValueError) as exc:
        raise ReleaseError("OWNER_UPLOAD or candidate artwork is not a canonical logical PNG") from exc
    if foreign or semi_alpha:
        raise ReleaseError("OWNER_UPLOAD source contains noncanonical color or alpha values")
    try:
        artwork = decode_logical_png(candidate_png)
    except (PNGContractError, TypeError, ValueError) as exc:
        raise ReleaseError("candidate artwork is not a canonical logical PNG") from exc
    if (not 20 <= source_width <= 59 or not 20 <= source_height <= 59
            or source_width != source_record.get("original_width")
            or source_height != source_record.get("original_height")
            or (artwork.width, artwork.height) != (source_width, source_height)
            or (candidate.get("width"), candidate.get("height")) != (source_width, source_height)):
        raise ReleaseError("OWNER_UPLOAD and candidate logical dimensions do not match exactly")
    source_grid_hash = logical_grid_hash(source_width, source_height, source_cells)
    candidate_grid_hash = logical_grid_hash(artwork.width, artwork.height, artwork.cells)
    if (artwork.cells != source_cells or candidate_grid_hash != source_grid_hash
            or candidate_grid_hash != candidate.get("grid_hash")
            or hashlib.sha256(candidate_png).hexdigest() != candidate.get("artwork_sha256")):
        raise ReleaseError("candidate logical artwork grid does not equal the exact OWNER_UPLOAD-derived grid")


def _verify_candidate_source_grid_binding(candidate: Mapping[str, Any], classification: Mapping[str, Any]) -> str:
    """Read and compare only this candidate's canonical source and artwork bytes."""

    from .. import studio_extensions as studio

    lineage = _candidate_source_lineage(candidate)
    source_id = lineage.get("source_id")
    expected_record = f"level_factory/output/owner-uploads/{source_id}/source.json"
    if lineage.get("source_record") != expected_record:
        raise ReleaseError("candidate source record path is not the canonical OWNER_UPLOAD path")
    try:
        record_path, source_path = studio._source_record_paths(str(source_id))
        repository = studio._repository_root().resolve()
        candidate_root = (repository / str(candidate.get("source_path", ""))).resolve()
        candidate_artwork = candidate_root / "artwork.png"
        if (not record_path.is_relative_to(repository) or not source_path.is_relative_to(repository)
                or not candidate_root.is_relative_to(repository)
                or not candidate_artwork.resolve().is_relative_to(repository)
                or record_path.is_symlink() or source_path.is_symlink() or candidate_artwork.is_symlink()
                or candidate_root.name != str(candidate.get("candidate_id", ""))):
            raise ReleaseError("candidate or OWNER_UPLOAD source path escaped the canonical repository")
        from ..semantic.normalization.core import RAW_ARTIFACT_MAX_BYTES
        if (source_path.stat().st_size > RAW_ARTIFACT_MAX_BYTES
                or candidate_artwork.stat().st_size > RAW_ARTIFACT_MAX_BYTES):
            raise ReleaseError("OWNER_UPLOAD or candidate artwork exceeds the bounded PNG byte policy")
        source_record = studio.verify_owner_source(str(source_id))
        source_png = source_path.read_bytes()
        candidate_png = candidate_artwork.read_bytes()
    except ReleaseError:
        raise
    except (OSError, TypeError, ValueError) as exc:
        raise ReleaseError("exact OWNER_UPLOAD source or candidate artwork bytes could not be read") from exc
    _validate_source_grid_bytes(candidate, classification, lineage, source_record, source_png, candidate_png)
    return str(lineage["source_sha256"])


def _official_challenge_vector(official: Mapping[str, Any]) -> list[float]:
    vector = official.get("challengeVector", official.get("challenge_vector", official.get("vector")))
    if isinstance(vector, Mapping):
        vector = [vector.get(axis) for axis in ("W", "C", "A", "U", "B", "R", "S")]
    if not isinstance(vector, (list, tuple)) or len(vector) != 7 or any(type(value) not in {int, float} or not math.isfinite(float(value)) for value in vector):
        raise ReleaseError("official Difficulty V1 challenge vector [W,C,A,U,B,R,S] is missing or malformed")
    return [float(value) for value in vector]


def _official_profile(official: Mapping[str, Any]) -> dict[str, Any]:
    profile = official.get("profile")
    if not isinstance(profile, Mapping) or profile.get("dominant") not in _DIFFICULTY_PROFILES:
        raise ReleaseError("official Difficulty V1 profile.dominant is missing or malformed")
    return dict(profile)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _supplement_path(run_id: str) -> Path:
    from .. import studio_extensions as studio
    safe = hashlib.sha256(run_id.encode("utf-8")).hexdigest()
    return studio.extensions_root() / "official-profile-supplements" / f"{safe}.json"


def _candidate_source_lineage(candidate: Mapping[str, Any]) -> dict[str, Any]:
    from .. import studio_extensions as studio
    bundle = (studio._repository_root() / str(candidate.get("source_path", ""))).resolve()
    repository = studio._repository_root().resolve()
    if not bundle.is_relative_to(repository) or bundle.name != str(candidate.get("candidate_id", "")):
        raise ReleaseError("candidate source lineage path is invalid")
    metadata = _json(bundle / "metadata.json")
    generator = metadata.get("generator_metadata", {})
    payload = generator.get("payload", {}) if isinstance(generator, Mapping) else {}
    data = payload.get("data", {}) if isinstance(payload, Mapping) else {}
    lineage = data.get("source_lineage", {}) if isinstance(data, Mapping) else {}
    if not isinstance(lineage, Mapping) or lineage.get("derivation") != "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE":
        raise ReleaseError("candidate lacks its exact owner-upload source lineage")
    return dict(lineage)


def _pinned_profile_from_godot(vector: list[float]) -> tuple[dict[str, Any], str]:
    from .game_rules import find_godot
    from . import pinned_game_source
    runtime = pinned_game_source.expected_runtime_root()
    pinned_game_source.verify_attested_runtime(runtime)
    executable = find_godot()
    if not executable:
        raise ReleaseError("Godot console runtime is unavailable for official profile derivation")
    probe = Path(__file__).resolve().parent / "godot" / "difficulty_profile_probe.gd"
    if not probe.is_file():
        raise ReleaseError("pinned profile probe source is unavailable")
    vector_object = dict(zip(("W", "C", "A", "U", "B", "R", "S"), vector, strict=True))
    command = [executable, "--headless", "--path", str(runtime), "--script", str(probe), "--", json.dumps(vector_object, separators=(",", ":"))]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=45, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReleaseError("pinned Difficulty V1 profile probe could not complete") from exc
    if result.returncode != 0:
        raise ReleaseError(f"pinned Difficulty V1 profile probe failed: {result.stderr[-300:]}")
    line = next((line for line in result.stdout.splitlines() if line.startswith("AUTHENTIC_V1_PROFILE:")), None)
    if line is None:
        raise ReleaseError("pinned Difficulty V1 profile probe returned no machine-readable profile")
    try:
        profile = json.loads(line.removeprefix("AUTHENTIC_V1_PROFILE:"))
    except json.JSONDecodeError as exc:
        raise ReleaseError("pinned Difficulty V1 profile probe returned malformed JSON") from exc
    return _official_profile({"profile": profile}), _hash(probe.read_bytes())


def _resolve_official_profile(candidate: Mapping[str, Any], pipeline: Mapping[str, Any], official: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Resolve direct analyzer output or an immutable, run-bound historical supplement."""
    if "profile" in official:
        return _official_profile(official), {"kind": "DIRECT", "supplement_path": None, "supplement_sha256": None}
    path = _supplement_path(str(pipeline.get("run_id", "")))
    if not path.is_file():
        raise ReleaseError("official Difficulty V1 profile.dominant is missing and no authenticated per-run supplement exists")
    supplement = _json(path)
    expected_digest = supplement.pop("supplement_digest", None)
    actual_digest = _hash(_canonical_bytes(supplement))
    supplement["supplement_digest"] = expected_digest
    from .. import studio_extensions as studio
    pipeline_path = studio._pipeline_path(str(pipeline.get("run_id", "")))
    pipeline_sha = _hash(pipeline_path.read_bytes()) if pipeline_path.is_file() else None
    source_id = pipeline.get("request", {}).get("source_id") if isinstance(pipeline.get("request"), Mapping) else None
    lineage = _candidate_source_lineage(candidate)
    source_record = studio._repository_root() / "level_factory" / "output" / "owner-uploads" / str(source_id) / "source.json"
    source_record_sha = _hash(source_record.read_bytes()) if source_record.is_file() else None
    vector = _official_challenge_vector(official)
    vector_sha = _hash(_canonical_bytes(vector))
    authority = pipeline.get("primary", {}).get("authority", {})
    from . import pinned_game_source
    try:
        attestation = pinned_game_source.verify_attested_runtime(pinned_game_source.expected_runtime_root())
    except (OSError, ValueError) as exc:
        raise ReleaseError("pinned game runtime authority is unavailable for historical profile proof") from exc
    analyzer_sha = next((item.get("sha256") for item in attestation["source_files"] if item.get("path") == "scripts/difficulty/level_difficulty_analyzer_v1.gd"), None)
    if (not source_id or lineage.get("source_id") != source_id or source_record_sha is None
            or lineage.get("source_record") != f"level_factory/output/owner-uploads/{source_id}/source.json"
            or lineage.get("source_sha256") != str(source_id).removeprefix("owner-upload-")
            or not isinstance(authority, Mapping)
            or authority.get("git_head") != attestation.get("source_commit")
            or authority.get("git_tree") != attestation.get("tree_sha")):
        raise ReleaseError("historical profile proof is not bound to the attested owner source and pinned game authority")
    expected = {
        "schema": "scrubbots-official-difficulty-v1-profile-supplement/v1",
        "disclosure": "AUTHENTIC_V1_PROFILE_DERIVED_LATER",
        "candidate_id": candidate.get("candidate_id"),
        "source_id": source_id,
        "source_record_sha256": source_record_sha,
        "run_id": pipeline.get("run_id"),
        "pipeline_sha256": pipeline_sha,
        "solver_supply_identity": pipeline.get("primary", {}).get("solver_supply_identity"),
        "vector": vector,
        "vector_sha256": vector_sha,
        "analyzer_sha256": analyzer_sha,
        "profile_probe_sha256": supplement.get("profile_probe_sha256"),
        "game_commit": attestation.get("source_commit"),
        "game_tree": attestation.get("tree_sha"),
        "profile": supplement.get("profile"),
        "method": "pinned LevelDifficultyAnalyzerV1.profile(vector), static pure function; computed twice and byte-identical",
    }
    expected["profile_probe_sha256"] = _hash((Path(__file__).resolve().parent / "godot" / "difficulty_profile_probe.gd").read_bytes())
    if (expected_digest != actual_digest or supplement.get("schema") != expected["schema"]
            or any(supplement.get(key) != value for key, value in expected.items() if key != "schema")):
        raise ReleaseError("historical official-profile supplement chain, analyzer authority, or digest does not match this immutable run")
    profile = _official_profile({"profile": supplement.get("profile")})
    return profile, {"kind": "DERIVED", "supplement_path": str(path), "supplement_sha256": _hash(path.read_bytes()), "supplement_digest": expected_digest}


def write_historical_profile_supplement(candidate: Mapping[str, Any], pipeline: Mapping[str, Any]) -> dict[str, Any]:
    """Persist a GDScript-computed profile as an immutable, later-derived supplement."""
    from .. import studio_extensions as studio
    run_id = str(pipeline.get("run_id", ""))
    pipeline_path = studio._pipeline_path(run_id)
    if not run_id or not pipeline_path.is_file() or _hash(pipeline_path.read_bytes()) != _hash(_canonical_bytes(pipeline) + b"\n"):
        # Windows newline/indentation can differ from canonical JSON serialization; exact original bytes are read below.
        try:
            current = _json(pipeline_path)
        except (OSError, ReleaseError):
            raise ReleaseError("cannot bind profile supplement to the exact persisted pipeline")
        if current != dict(pipeline):
            raise ReleaseError("cannot bind profile supplement to the exact persisted pipeline")
    official = _canonical_official_difficulty(pipeline["primary"])
    vector = _official_challenge_vector(official)
    first_profile, probe_sha = _pinned_profile_from_godot(vector)
    second_profile, second_probe_sha = _pinned_profile_from_godot(vector)
    if first_profile != second_profile or probe_sha != second_probe_sha:
        raise ReleaseError("pinned Difficulty V1 profile computation was not repeatable")
    from . import pinned_game_source
    runtime = pinned_game_source.expected_runtime_root()
    attestation = pinned_game_source.verify_attested_runtime(runtime)
    analyzer_sha = next(item["sha256"] for item in attestation["source_files"] if item["path"] == "scripts/difficulty/level_difficulty_analyzer_v1.gd")
    source_id = pipeline.get("request", {}).get("source_id")
    lineage = _candidate_source_lineage(candidate)
    source_record = studio._repository_root() / "level_factory" / "output" / "owner-uploads" / str(source_id) / "source.json"
    authority = pipeline.get("primary", {}).get("authority", {})
    if (not source_id or lineage.get("source_id") != source_id or not source_record.is_file()
            or lineage.get("source_record") != f"level_factory/output/owner-uploads/{source_id}/source.json"
            or lineage.get("source_sha256") != str(source_id).removeprefix("owner-upload-")
            or not isinstance(authority, Mapping)
            or authority.get("git_head") != attestation.get("source_commit")
            or authority.get("git_tree") != attestation.get("tree_sha")):
        raise ReleaseError("cannot supplement a profile without the exact owner source record and pinned game identity")
    payload = {
        "schema": "scrubbots-official-difficulty-v1-profile-supplement/v1",
        "disclosure": "AUTHENTIC_V1_PROFILE_DERIVED_LATER",
        "candidate_id": candidate.get("candidate_id"),
        "source_id": source_id,
        "source_record_sha256": _hash(source_record.read_bytes()) if source_record.is_file() else None,
        "run_id": run_id,
        "pipeline_sha256": _hash(pipeline_path.read_bytes()),
        "solver_supply_identity": pipeline.get("primary", {}).get("solver_supply_identity"),
        "vector": vector,
        "vector_sha256": _hash(_canonical_bytes(vector)),
        "analyzer_sha256": analyzer_sha,
        "profile_probe_sha256": probe_sha,
        "game_commit": attestation.get("source_commit"),
        "game_tree": attestation.get("tree_sha"),
        "profile": first_profile,
        "method": "pinned LevelDifficultyAnalyzerV1.profile(vector), static pure function; computed twice and byte-identical",
    }
    payload["supplement_digest"] = _hash(_canonical_bytes(payload))
    path = _supplement_path(run_id)
    raw = _canonical_bytes(payload) + b"\n"
    if path.exists() and path.read_bytes() != raw:
        raise ReleaseError("a different immutable profile supplement already exists for this run")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_bytes(raw)
    if path.read_bytes() != raw:
        raise ReleaseError("historical profile supplement failed exact durable read-back")
    return {"path": str(path), "sha256": _hash(raw), "supplement_digest": payload["supplement_digest"]}


def _validate_score_and_class(primary: Mapping[str, Any], official: Mapping[str, Any], provenance: Mapping[str, Any]) -> None:
    score = official.get("challengeScore")
    difficulty = primary.get("difficulty", {})
    stored_score = difficulty.get("score") if isinstance(difficulty, Mapping) else None
    if type(score) not in {int, float} or not math.isfinite(float(score)) or type(stored_score) not in {int, float} or not math.isfinite(float(stored_score)):
        raise ReleaseError("official Difficulty V1 challengeScore and primary difficulty score are required finite numbers")
    if provenance.get("kind") == "DERIVED":
        if float(stored_score) != round(float(score), 2):
            raise ReleaseError("historical rounded Difficulty V1 score does not match the evidenced two-decimal rule")
    elif float(stored_score) != float(score):
        raise ReleaseError("direct official Difficulty V1 challengeScore must exactly equal primary difficulty score")
    from . import pinned_game_source
    from .game_rules import GameRules
    try:
        rules = GameRules(pinned_game_source.expected_runtime_root(), column_count=int(primary.get("column_count", 3)))
    except (OSError, RuntimeError, ValueError) as exc:
        raise ReleaseError("pinned Difficulty V1 class authority is unavailable") from exc
    if not isinstance(difficulty, Mapping) or difficulty.get("class") != rules.classify(float(score)):
        raise ReleaseError("stored difficulty class does not match the pinned Difficulty V1 class authority")


def _canonical_official_difficulty(primary: Mapping[str, Any]) -> dict[str, Any]:
    """Read the official V1 object from the canonical primary result shape."""
    result = primary.get("result", {})
    result = result if isinstance(result, Mapping) else {}
    metrics = result.get("solver_metrics", primary.get("solver_metrics", {}))
    official = metrics.get("official_difficulty_v1", {}) if isinstance(metrics, Mapping) else {}
    if not isinstance(official, Mapping) or official.get("ok") is not True:
        raise ReleaseError("official Difficulty V1 evidence is missing or malformed")
    return dict(official)


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReleaseError(f"release authority is unavailable: {path}") from exc
    if not isinstance(value, dict): raise ReleaseError(f"release authority is malformed: {path}")
    return value


def _hash(raw: bytes) -> str: return hashlib.sha256(raw).hexdigest()


def _level_content_hash(path: Path) -> str:
    # Git's text checkout may convert JSON line endings on Windows. Official
    # game evidence binds the canonical LF file content, so ignore CRLF-only
    # checkout conversion while still rejecting any content change.
    return _hash(path.read_bytes().replace(b"\r\n", b"\n"))


def _pool_root() -> Path:
    from .. import studio_extensions as studio
    return studio.extensions_root() / "release-pool"


def enter_release_pool(candidate: Mapping[str, Any], pipeline: Mapping[str, Any], review: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if pipeline.get("disposition") != "READY" or pipeline.get("primary", {}).get("state") != "READY":
        return {"disposition": "NOT_ENTERED_NOT_READY", "reason": "Release Pool requires a canonical READY ZIP/solver/replay/Difficulty pipeline."}
    classification = validate_pool_candidate_provenance(candidate, review)
    from .. import studio_extensions as studio
    lineage = _candidate_source_lineage(candidate)
    source_id = lineage.get("source_id")
    try:
        source_record = studio.verify_owner_source(str(source_id))
    except (OSError, ValueError, TypeError) as exc:
        raise ReleaseError("canonical OWNER_UPLOAD source record and bytes could not be reverified") from exc
    if (source_record.get("source_sha256") != classification.get("source_sha256")
            or source_record.get("source_bytes_sha256") != classification.get("source_sha256")):
        raise ReleaseError("candidate classification does not match the current immutable OWNER_UPLOAD bytes")
    primary = pipeline["primary"]
    difficulty = primary.get("difficulty", {})
    official = _canonical_official_difficulty(primary)
    vector = _official_challenge_vector(official)
    profile, profile_provenance = _resolve_official_profile(candidate, pipeline, official)
    _validate_score_and_class(primary, official, profile_provenance)
    official_score = official.get("challengeScore")
    if type(official_score) not in {int, float} or not math.isfinite(float(official_score)):
        raise ReleaseError("official Difficulty V1 challengeScore is missing or malformed")
    if not isinstance(difficulty, Mapping) or difficulty.get("class") is None:
        raise ReleaseError("official Difficulty V1 class is missing")
    dominant = profile["dominant"]
    bundle_path = (studio._repository_root() / str(candidate["source_path"])).resolve()
    paths = {"artwork": bundle_path / "artwork.png", "level": Path(str(primary.get("files", {}).get("level", ""))).expanduser(), "supply_plan": Path(str(primary.get("files", {}).get("supply_plan", ""))).expanduser()}
    if any(not path.is_file() for path in paths.values()): raise ReleaseError("Release Pool requires existing canonical artwork, level, and supply files")
    file_digests = {name: {"path": str(path), "sha256": _hash(path.read_bytes())} for name, path in paths.items()}
    payload = {
        "schema": "scrubbots-release-pool-entry/v1", "candidate_id": candidate["candidate_id"],
        "width": candidate.get("width"), "height": candidate.get("height"), "used_colors": candidate.get("used_colors", []),
        "artwork_sha256": candidate["artwork_sha256"], "grid_hash": candidate["grid_hash"],
        "challenge_score": float(official_score), "difficulty_class": difficulty.get("class"),
        "challenge_vector": vector, "dominant_profile": dominant, "official_profile": profile,
        "official_profile_provenance": profile_provenance,
        "frustration_risk": official.get("frustrationRisk") if isinstance(official, Mapping) else None,
        "session_load": official.get("sessionLoad") if isinstance(official, Mapping) else None,
        "signature": {"dimensions": [candidate.get("width"), candidate.get("height")], "paletteSet": candidate.get("used_colors", []), "challengeVector": vector, "dominantProfile": dominant, "silhouetteHash": candidate.get("grid_hash")},
        "files": file_digests, "pipeline_run_id": pipeline["run_id"], "pipeline_sha256": _hash(studio._pipeline_path(str(pipeline["run_id"])).read_bytes()),
        "review_id": review.get("review_id") if review is not None else None,
        "eligibility_source": "OWNER_ACCEPT" if review is not None else "READY_AUTO",
        "candidate_classification": classification,
        "source_bundle": candidate["source_path"], "candidate": dict(candidate), "pipeline": dict(pipeline),
    }
    payload["entry_digest"] = _hash(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
    path = _pool_root() / f"{candidate['candidate_id']}-{pipeline['run_id']}-{review.get('review_id') if review is not None else 'ready'}.json"
    raw = (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if path.exists() and path.read_bytes() != raw:
        raise ReleaseError("candidate already has different immutable Release Pool evidence")
    path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
    return {"disposition": "ENTERED_RELEASE_POOL", "candidate_id": candidate["candidate_id"], "entry_digest": payload["entry_digest"], "pool_size": len(list(_pool_root().glob("*.json")))}


def release_entries(candidate_id_filter: str | None = None) -> list[dict[str, Any]]:
    entries = []
    from .. import studio_extensions as studio
    for path in sorted(_pool_root().glob("*.json")) if _pool_root().exists() else ():
        value = _json(path)
        expected = value.pop("entry_digest", None)
        actual = _hash(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
        value["entry_digest"] = expected
        if expected != actual: raise ReleaseError(f"Release Pool entry digest mismatch: {path.name}")
        candidate_id = str(value.get("candidate_id", ""))
        if candidate_id_filter is not None and candidate_id != candidate_id_filter:
            continue
        latest = studio._latest_review(candidate_id)
        if latest and latest.get("disposition") == "REJECT":
            continue
        if not _eligibility_matches_current_review(value, latest):
            continue
        current_run = studio._latest_ready_pipeline(candidate_id)
        if current_run is None or current_run.get("run_id") != value.get("pipeline_run_id"):
            continue
        pipeline_path = studio._pipeline_path(str(value.get("pipeline_run_id", "")))
        if not pipeline_path.is_file() or _hash(pipeline_path.read_bytes()) != value.get("pipeline_sha256"):
            raise ReleaseError(f"Release Pool pipeline evidence changed or disappeared: {path.name}")
        pipeline = _json(pipeline_path)
        primary = pipeline.get("primary", {})
        official = _canonical_official_difficulty(primary)
        resolved_profile, provenance = _resolve_official_profile(value.get("candidate", {}), pipeline, official)
        _validate_score_and_class(primary, official, provenance)
        if (resolved_profile != value.get("official_profile")
                or provenance != value.get("official_profile_provenance")
                or _official_challenge_vector(official) != value.get("challenge_vector")
                or float(official.get("challengeScore")) != value.get("challenge_score")
                or primary.get("difficulty", {}).get("class") != value.get("difficulty_class")):
            raise ReleaseError(f"Release Pool Difficulty V1 proof no longer matches its immutable pipeline: {path.name}")
        current_candidate = next((item for item in studio.list_candidates() if item.get("candidate_id") == candidate_id), None)
        if current_candidate is None or current_candidate.get("artwork_sha256") != value.get("artwork_sha256") or current_candidate.get("grid_hash") != value.get("grid_hash"):
            raise ReleaseError(f"Release Pool candidate identity changed or disappeared: {path.name}")
        # Existing pre-classification entries remain read-only historical evidence.
        # Newly created entries always carry classification and must revalidate it.
        if value.get("candidate_classification") is not None:
            source = value.get("eligibility_source")
            if source == "OWNER_ACCEPT" and (not isinstance(latest, Mapping) or latest.get("disposition") != "ACCEPT"):
                continue
            if source == "READY_AUTO" and isinstance(latest, Mapping) and latest.get("disposition") == "REJECT":
                continue
            if source not in {"OWNER_ACCEPT", "READY_AUTO"}:
                continue
            try:
                classification = validate_pool_candidate_provenance(
                    current_candidate, latest if source == "OWNER_ACCEPT" else None
                )
            except ReleaseError:
                continue
            if value.get("candidate_classification") != classification:
                raise ReleaseError(f"Release Pool candidate classification changed or disappeared: {path.name}")
            if value.get("candidate", {}).get("candidate_id") != candidate_id:
                raise ReleaseError(f"Release Pool candidate payload identity changed: {path.name}")
        for name, file_record in value.get("files", {}).items():
            evidence_file = Path(str(file_record.get("path", "")))
            if not evidence_file.is_file() or _hash(evidence_file.read_bytes()) != file_record.get("sha256"):
                raise ReleaseError(f"Release Pool {name} artifact changed or disappeared: {path.name}")
        entries.append(value)
    by_candidate: dict[str, dict[str, Any]] = {}
    for entry in entries:
        candidate_id = str(entry["candidate_id"])
        current = by_candidate.get(candidate_id)
        if current is None or (entry.get("eligibility_source") == "OWNER_ACCEPT" and current.get("eligibility_source") != "OWNER_ACCEPT"):
            by_candidate[candidate_id] = entry
    return [by_candidate[key] for key in sorted(by_candidate)]


def _eligibility_matches_current_review(entry: Mapping[str, Any], latest_review: Mapping[str, Any] | None) -> bool:
    """Keep immutable pool eligibility consistent with the current review authority."""
    source = entry.get("eligibility_source")
    review_id = entry.get("review_id")
    if source == "READY_AUTO":
        return review_id is None and not (
            isinstance(latest_review, Mapping) and latest_review.get("disposition") == "REJECT"
        )
    if source == "OWNER_ACCEPT":
        return (
            isinstance(review_id, str) and bool(review_id)
            and isinstance(latest_review, Mapping)
            and latest_review.get("disposition") == "ACCEPT"
            and latest_review.get("review_id") == review_id
        )
    return False


def _production_release_entries() -> list[dict[str, Any]]:
    """Return only explicitly classified, currently owner-accepted production entries."""

    from .. import studio_extensions as studio

    eligible: list[dict[str, Any]] = []
    for entry in release_entries():
        classification = entry.get("candidate_classification")
        candidate_id = str(entry.get("candidate_id", ""))
        latest = studio._latest_review(candidate_id)
        if (not isinstance(classification, Mapping)
                or classification.get("candidate_class") != CandidateClass.PRODUCTION_CANDIDATE.value
                or entry.get("eligibility_source") != "OWNER_ACCEPT"
                or not _eligibility_matches_current_review(entry, latest)
                or entry.get("review_id") != latest.get("review_id")
                or not isinstance(entry.get("candidate"), Mapping)
                or entry["candidate"].get("candidate_id") != candidate_id):
            continue
        eligible.append(entry)
    return eligible


def _game_authority(game: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    authority = load_progression_authority(game)
    analyzer_path = game / "data/config/level_difficulty_analysis_v1.json"
    analyzer = _json(analyzer_path)
    docs_path = game / "docs/10_LEVEL_FACTORY_GENERATION_SCORING_ARCHITECTURE.md"
    docs = docs_path.read_bytes()
    difficulty_rules_path = game / "scripts/data/difficulty_rules.gd"
    difficulty_rules = difficulty_rules_path.read_text(encoding="utf-8")
    minimum = re.search(r"const ENVELOPE_MIN\s*:=\s*(\d+)", difficulty_rules)
    maximum = re.search(r"const ENVELOPE_MAX\s*:=\s*(\d+)", difficulty_rules)
    palette_rules_path = game / "docs/08_PIXEL_ART_PALETTE_RULES.md"
    palette_rules = palette_rules_path.read_text(encoding="utf-8")
    color_range = re.search(r"global\s+(\d+)\.\.(\d+)\s+used-color envelope", palette_rules)
    if not minimum or not maximum or not color_range:
        raise ReleaseError("current game production dimension/color envelope cannot be derived from authoritative code/docs")
    authority["_production_envelope"] = {"min_dimension": int(minimum.group(1)), "max_dimension": int(maximum.group(1)), "min_colors": int(color_range.group(1)), "max_colors": int(color_range.group(2))}
    authority["_m10_rules"] = {"analysis_sha256": _hash(analyzer_path.read_bytes()), "architecture_sha256": _hash(docs), "difficulty_rules_sha256": _hash(difficulty_rules.encode()), "palette_rules_sha256": _hash(palette_rules.encode()), "similarity_definition": analyzer.get("operationalDefinitions", {}).get("similarity"), "profile_definition": analyzer.get("operationalDefinitions", {}).get("profiles")}
    catalog_path = game / "data/levels/catalog/production_catalog_v1.json"
    catalog = _json(catalog_path)
    entries = [entry for entry in catalog.get("entries", []) if isinstance(entry, Mapping) and type(entry.get("order")) is int]
    ordered = sorted(entries, key=lambda item: int(item["order"]))
    required_tail = ordered[-2:]
    evidence_path = game / "coordination/sessions/M53-C001/evidence/first10_difficulty_v1.json"
    evidence: dict[str, Any] = {}
    if evidence_path.is_file():
        evidence = _json(evidence_path)
        provenance = evidence.get("provenance", {})
        if (evidence.get("schema") != "scrubbots.m53.first10_difficulty.v1"
            or not isinstance(provenance, Mapping)
            or provenance.get("analyzerVersion") != analyzer.get("analyzerVersion")
            or evidence.get("analysisConfig") != analyzer):
            evidence = {}
    evidence_by_identity = {
        (record.get("order"), record.get("id")): record
        for record in evidence.get("levels", [])
        if isinstance(record, Mapping)
    }

    def canonical_tail(entry: Mapping[str, Any], metadata: Mapping[str, Any], official: Mapping[str, Any], *, evidence_source: str) -> dict[str, Any] | None:
        level_path = game / str(entry.get("level_path", "")).removeprefix("res://")
        if not level_path.is_file():
            return None
        level_sha = _level_content_hash(level_path)
        file_digests = metadata.get("fileDigests", {})
        official_level_sha = official.get("levelSha256") if isinstance(official, Mapping) else None
        bound_level_sha = file_digests.get("level") if isinstance(file_digests, Mapping) else None
        if bound_level_sha != level_sha and official_level_sha != level_sha:
            return None
        try:
            profile = _official_profile(official)
            vector = _official_challenge_vector(official)
        except ReleaseError:
            return None
        score = official.get("challengeScore", metadata.get("challengeScore"))
        if type(score) not in {int, float} or not math.isfinite(float(score)):
            return None
        dimensions = [metadata.get("width"), metadata.get("height")]
        if any(type(value) is not int or value < 1 for value in dimensions):
            return None
        progression = metadata.get("progression", {})
        progression = progression if isinstance(progression, Mapping) else {}
        signature = metadata.get("noveltySignature", official.get("signature"))
        if not isinstance(signature, Mapping):
            return None
        palette = signature.get("paletteSet", metadata.get("paletteSet", metadata.get("palette", [])))
        signature_dimensions = signature.get("dimensions", dimensions)
        signature_vector = signature.get("challengeVector", vector)
        if (not isinstance(palette, list) or not palette
            or signature_dimensions != dimensions
            or not isinstance(signature_vector, (list, tuple)) or len(signature_vector) != 7
            or any(type(value) not in {int, float} or not math.isfinite(float(value)) for value in signature_vector)):
            return None
        bound_signature = {
            **dict(signature),
            "dimensions": dimensions,
            "paletteSet": list(palette),
            "challengeVector": [float(value) for value in signature_vector],
            "dominantProfile": profile["dominant"],
        }
        return {
            "order": int(entry["order"]), "candidate_id": str(entry.get("id", "")),
            "challenge_score": float(score), "dominant_profile": profile["dominant"],
            "official_profile": profile, "challenge_vector": vector,
            "frustration_risk": official.get("frustrationRisk", metadata.get("frustrationRisk")),
            "slot": progression.get("slot", metadata.get("slot")),
            "width": dimensions[0], "height": dimensions[1], "palette": list(palette),
            "signature": bound_signature, "level_sha256": level_sha, "evidence_source": evidence_source,
        }

    catalog_tail: list[dict[str, Any]] = []
    for entry in required_tail:
        metadata_path = str(entry.get("metadata_path", "")).removeprefix("res://")
        metadata_file = game / metadata_path if metadata_path else None
        metadata = _json(metadata_file) if metadata_file is not None and metadata_file.is_file() else {}
        official = metadata.get("official_difficulty_v1", metadata.get("officialDifficultyV1", {}))
        resolved = canonical_tail(entry, metadata, official, evidence_source="catalog metadata") if isinstance(official, Mapping) else None
        if resolved is None:
            record = evidence_by_identity.get((entry.get("order"), entry.get("id")))
            level_path = game / str(entry.get("level_path", "")).removeprefix("res://")
            if isinstance(record, Mapping) and level_path.is_file() and record.get("levelSha256") == _level_content_hash(level_path):
                evidence_vector = record.get("vector")
                signature_vector = [evidence_vector.get(axis) for axis in ("W", "C", "A", "U", "B", "R", "S")] if isinstance(evidence_vector, Mapping) else evidence_vector
                record_metadata = {"width": record.get("width"), "height": record.get("height"), "palette": record.get("palette"), "slot": record.get("slot"), "challengeScore": record.get("challengeScore"), "noveltySignature": {"dimensions": [record.get("width"), record.get("height")], "paletteSet": record.get("palette"), "challengeVector": signature_vector}}
                record_official = {"levelSha256": record.get("levelSha256"), "challengeScore": record.get("challengeScore"), "vector": record.get("vector"), "profile": record.get("profile"), "frustrationRisk": record.get("frustrationRisk")}
                resolved = canonical_tail(entry, record_metadata, record_official, evidence_source="current-game M53 Difficulty V1 evidence")
        if resolved is None:
            raise ReleaseError(f"CATALOG_TAIL_DIFFICULTY_EVIDENCE_UNAVAILABLE: order {entry.get('order')} ({entry.get('id')}) has no hash-bound official Difficulty V1 profile/vector/signature")
        catalog_tail.append(resolved)
    if catalog_tail:
        authority["_catalog_tail"] = catalog_tail
        authority["_m10_rules"]["catalog_tail_difficulty_evidence_sha256"] = _hash(evidence_path.read_bytes()) if evidence_path.is_file() and any(item["evidence_source"].startswith("current-game M53") for item in catalog_tail) else None
    return catalog, authority


def build_release_plan(*, game_project: str | Path | None = None, k: int = 100, locks: Mapping[int, str] | None = None) -> dict[str, Any]:
    game = discover_game_project(game_project)
    catalog, authority = _game_authority(game)
    entries = _production_release_entries()
    plan = build_campaign_plan(catalog=catalog, authority=authority, pool=entries, k=k, locks=locks)
    from .. import studio_extensions as studio
    plan_path = studio.extensions_root() / "release" / "campaign_plan.json"
    write_campaign_plan(plan_path, plan)
    plan["artifact_path"] = str(plan_path)
    plan["pool_size"] = len(entries)
    return plan


def validate_release_plan(*, plan_hash: str, game_project: str | Path | None = None) -> dict[str, Any]:
    """Read-only revalidation of the exact current CampaignBuilder plan and inputs."""
    game = discover_game_project(game_project)
    from .. import studio_extensions as studio
    plan_path = studio.extensions_root() / "release" / "campaign_plan.json"
    plan = _json(plan_path)
    if plan.get("plan_hash") != plan_hash: raise ReleaseError("APPROVE requires the current exact campaign plan hash")
    entries = {entry["candidate_id"]: entry for entry in _production_release_entries()}
    rows = plan.get("slots", [])
    prefix = []
    for row in rows:
        if not row.get("chosen_id"): break
        prefix.append(row)
    if not prefix: raise ReleaseError("campaign plan has no publishable contiguous prefix")
    missing = [str(row.get("chosen_id", "")) for row in prefix if str(row.get("chosen_id", "")) not in entries]
    if missing:
        raise ReleaseError("campaign plan selected a legacy or no-longer-eligible Pool entry")
    numbers = [int(row["n"]) for row in prefix]
    if numbers != list(range(numbers[0], numbers[0] + len(numbers))): raise ReleaseError("campaign plan prefix is not contiguous")
    catalog, authority = _game_authority(game)
    locks = {int(row["n"]): str(row["chosen_id"]) for row in prefix}
    rebuilt = build_campaign_plan(catalog=catalog, authority=authority, pool=list(entries.values()), k=int(plan["K"]), locks=locks)
    if rebuilt.get("plan_hash") != plan_hash: raise ReleaseError("campaign inputs or locked sequence changed since plan review")
    items = []
    for row in prefix:
        entry = entries[str(row["chosen_id"])]
        bundle = (studio._repository_root() / str(entry["source_bundle"])).resolve()
        latest = studio._latest_review(str(row["chosen_id"]))
        try:
            classification = validate_pool_candidate_provenance(entry["candidate"], latest)
        except (KeyError, TypeError, ReleaseError) as exc:
            raise ReleaseError("selected campaign candidate failed current OWNER_UPLOAD provenance revalidation") from exc
        if classification != entry.get("candidate_classification"):
            raise ReleaseError("selected campaign candidate classification changed since Pool entry")
        items.append({"candidate": entry["candidate"], "pipeline": entry["pipeline"], "source_bundle": bundle, "level_number": int(row["n"])})
    return {"game_project": game, "plan": plan, "prefix": prefix, "items": items}


def approve_release_plan(*, plan_hash: str, game_project: str | Path | None = None) -> dict[str, Any]:
    validated = validate_release_plan(plan_hash=plan_hash, game_project=game_project)
    try:
        result = publish_batch(game_project=validated["game_project"], items=validated["items"])
    except (PublicationError, OSError, ValueError) as exc:
        raise ReleaseError(str(exc)) from exc
    prefix = validated["prefix"]
    return {**result, "plan_hash": plan_hash, "approved_orders": [row["n"] for row in prefix]}


__all__ = ["ReleaseError", "approve_release_plan", "build_release_plan", "enter_release_pool", "release_entries", "validate_release_plan"]
