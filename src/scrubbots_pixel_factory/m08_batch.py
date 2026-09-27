"""Offline, deterministic M08 production-batch evidence contracts.

M08 is an envelope around the accepted generator, M03/M04/M05 evidence and
M08 output bundles.  It intentionally does not compile levels, solve puzzles,
render artwork, or create a second owner-review store.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from pathlib import PurePosixPath
from typing import Any, Callable, Iterable, Mapping

from .difficulty_analysis import LaneClass

SCHEMA = "scrubbots-m08-production-batch"
VERSION = 1
HANDOFF_SCHEMA = "scrubbots-m08-content-pipeline-handoff"
HANDOFF_VERSION = 1
POLICY_VERSION = "M08_FACTORY_ACCEPTANCE_V1"
_DISPOSITIONS = {"ACCEPT", "REJECT", "INCONCLUSIVE", "UNAVAILABLE", "ERROR"}
_ATTEMPT_DISPOSITIONS = {"ACCEPT", "REJECT", "DUPLICATE", "INCONCLUSIVE", "UNAVAILABLE", "ERROR"}


class M08ContractError(ValueError):
    """Raised when a production evidence contract is malformed or stale."""


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Mapping[str, Any] | bytes | str) -> str:
    if isinstance(value, Mapping):
        value = _canonical(value)
    elif isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _sha(value: Any, label: str) -> str:
    if type(value) is not str or len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
        raise M08ContractError(f"{label} must be a lowercase SHA-256")
    return value


def _safe_ref(value: Any, label: str, *, allow_none: bool = False) -> str | None:
    if value is None and allow_none:
        return None
    if type(value) is not str or not value or value.startswith("/") or ":" in value or "\\" in value:
        raise M08ContractError(f"{label} must be a safe portable relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.parts == ():
        raise M08ContractError(f"{label} may not traverse directories")
    return value


def _lane(value: Any) -> LaneClass:
    try:
        return value if isinstance(value, LaneClass) else LaneClass(value)
    except (TypeError, ValueError) as exc:
        raise M08ContractError("unsupported M04 lane/class") from exc


@dataclass(frozen=True, slots=True)
class LaneRequest:
    lane: LaneClass
    requested_accepted: int
    attempt_budget: int

    def __post_init__(self) -> None:
        if not isinstance(self.lane, LaneClass) or type(self.requested_accepted) is not int or self.requested_accepted < 0:
            raise M08ContractError("lane request count is malformed")
        if type(self.attempt_budget) is not int or self.attempt_budget < 1 or self.requested_accepted > self.attempt_budget:
            raise M08ContractError("lane request must have a finite budget covering its target")

    def as_dict(self) -> dict[str, Any]:
        return {"lane": self.lane.value, "requested_accepted": self.requested_accepted, "attempt_budget": self.attempt_budget}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "LaneRequest":
        if set(value) != {"lane", "requested_accepted", "attempt_budget"}:
            raise M08ContractError("lane request fields are unsupported or incomplete")
        return cls(_lane(value["lane"]), value["requested_accepted"], value["attempt_budget"])


@dataclass(frozen=True, slots=True)
class BatchPlan:
    cadence: tuple[LaneRequest, ...]
    root_seed: int
    seed_namespace: str
    generation_policy: str = POLICY_VERSION
    m04_lane_policy: str = "SCORE_LANE_V1"
    environment_identity: str = "LOCAL_OFFLINE_FACTORY"
    provenance_policy: str = "M03_M04_M05_M07_BOUND_V1"
    schema: str = SCHEMA
    version: int = VERSION

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.version != VERSION or not self.cadence:
            raise M08ContractError("plan schema/cadence is malformed")
        if len({item.lane for item in self.cadence}) != len(self.cadence):
            raise M08ContractError("lane cadence must not repeat a lane")
        if type(self.root_seed) is not int or type(self.seed_namespace) is not str or not self.seed_namespace.strip():
            raise M08ContractError("plan seed identity is malformed")
        for value, label in ((self.generation_policy, "generation policy"), (self.m04_lane_policy, "M04 lane policy"), (self.environment_identity, "environment identity"), (self.provenance_policy, "provenance policy")):
            if type(value) is not str or not value.strip():
                raise M08ContractError(f"{label} is required")

    def as_dict(self) -> dict[str, Any]:
        return {"schema": self.schema, "version": self.version, "cadence": [item.as_dict() for item in self.cadence], "root_seed": self.root_seed, "seed_namespace": self.seed_namespace, "generation_policy": self.generation_policy, "m04_lane_policy": self.m04_lane_policy, "environment_identity": self.environment_identity, "provenance_policy": self.provenance_policy}

    def digest(self) -> str:
        return digest(self.as_dict())

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "BatchPlan":
        required = {"schema", "version", "cadence", "root_seed", "seed_namespace", "generation_policy", "m04_lane_policy", "environment_identity", "provenance_policy"}
        if set(value) != required or not isinstance(value["cadence"], list):
            raise M08ContractError("plan fields are unsupported or incomplete")
        return cls(tuple(LaneRequest.from_dict(item) for item in value["cadence"]), value["root_seed"], value["seed_namespace"], value["generation_policy"], value["m04_lane_policy"], value["environment_identity"], value["provenance_policy"], value["schema"], value["version"])


@dataclass(frozen=True, slots=True)
class CandidateEvidence:
    """All current M03/M04/M05/M07 and canonical M08 identities for one candidate."""

    candidate_id: str
    lane: LaneClass
    m03_disposition: str
    m03_digest: str
    m04_disposition: str
    m04_digest: str
    m04_lane_digest: str
    m05_disposition: str
    m05_digest: str
    level_data_digest: str
    logical_art_digest: str
    source_provenance_digest: str
    generation_request_digest: str
    generation_result_digest: str
    generation_metadata_digest: str
    bundle_digest: str
    level_data_ref: str
    logical_art_ref: str
    bundle_ref: str
    source_provenance_ref: str
    m03_ref: str
    m04_ref: str
    m05_ref: str
    generation_ref: str
    preview_digest: str | None = None
    preview_ref: str | None = None
    mutation_digest: str | None = None
    mutation_ref: str | None = None

    def __post_init__(self) -> None:
        if type(self.candidate_id) is not str or not self.candidate_id.strip() or not isinstance(self.lane, LaneClass):
            raise M08ContractError("candidate identity/lane is malformed")
        if self.m03_disposition != "ACCEPT" or self.m04_disposition != "ACCEPT" or self.m05_disposition != "ACCEPT":
            raise M08ContractError("only current M03/M04/M05 ACCEPT evidence can form a Factory-accepted candidate")
        for value, label in ((self.m03_digest, "M03"), (self.m04_digest, "M04"), (self.m04_lane_digest, "M04 lane"), (self.m05_digest, "M05 QA"), (self.level_data_digest, "LevelData"), (self.logical_art_digest, "logical art"), (self.source_provenance_digest, "source provenance"), (self.generation_request_digest, "generation request"), (self.generation_result_digest, "generation result"), (self.generation_metadata_digest, "generation metadata"), (self.bundle_digest, "bundle")):
            _sha(value, label)
        for value, label in ((self.preview_digest, "preview"), (self.mutation_digest, "M07 mutation")):
            if value is not None:
                _sha(value, label)
        for value, label in ((self.level_data_ref, "LevelData ref"), (self.logical_art_ref, "logical art ref"), (self.bundle_ref, "bundle ref"), (self.source_provenance_ref, "source ref"), (self.m03_ref, "M03 ref"), (self.m04_ref, "M04 ref"), (self.m05_ref, "M05 ref"), (self.generation_ref, "generation ref")):
            _safe_ref(value, label)
        _safe_ref(self.preview_ref, "preview ref", allow_none=True)
        _safe_ref(self.mutation_ref, "mutation ref", allow_none=True)
        if (self.preview_digest is None) != (self.preview_ref is None) or (self.mutation_digest is None) != (self.mutation_ref is None):
            raise M08ContractError("optional preview/mutation identity must be explicit and paired")

    def as_dict(self) -> dict[str, Any]:
        return {"candidate_id": self.candidate_id, "lane": self.lane.value, "m03_disposition": self.m03_disposition, "m03_digest": self.m03_digest, "m04_disposition": self.m04_disposition, "m04_digest": self.m04_digest, "m04_lane_digest": self.m04_lane_digest, "m05_disposition": self.m05_disposition, "m05_digest": self.m05_digest, "level_data_digest": self.level_data_digest, "logical_art_digest": self.logical_art_digest, "source_provenance_digest": self.source_provenance_digest, "generation_request_digest": self.generation_request_digest, "generation_result_digest": self.generation_result_digest, "generation_metadata_digest": self.generation_metadata_digest, "bundle_digest": self.bundle_digest, "level_data_ref": self.level_data_ref, "logical_art_ref": self.logical_art_ref, "bundle_ref": self.bundle_ref, "source_provenance_ref": self.source_provenance_ref, "m03_ref": self.m03_ref, "m04_ref": self.m04_ref, "m05_ref": self.m05_ref, "generation_ref": self.generation_ref, "preview_digest": self.preview_digest, "preview_ref": self.preview_ref, "mutation_digest": self.mutation_digest, "mutation_ref": self.mutation_ref}

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "CandidateEvidence":
        fields = set(cls.__dataclass_fields__)
        if set(value) != fields:
            raise M08ContractError("candidate evidence fields are unsupported or incomplete")
        return cls(value["candidate_id"], _lane(value["lane"]), value["m03_disposition"], value["m03_digest"], value["m04_disposition"], value["m04_digest"], value["m04_lane_digest"], value["m05_disposition"], value["m05_digest"], value["level_data_digest"], value["logical_art_digest"], value["source_provenance_digest"], value["generation_request_digest"], value["generation_result_digest"], value["generation_metadata_digest"], value["bundle_digest"], value["level_data_ref"], value["logical_art_ref"], value["bundle_ref"], value["source_provenance_ref"], value["m03_ref"], value["m04_ref"], value["m05_ref"], value["generation_ref"], value["preview_digest"], value["preview_ref"], value["mutation_digest"], value["mutation_ref"])


@dataclass(frozen=True, slots=True)
class AcceptedBatchEntry:
    plan_digest: str
    lane: LaneClass
    attempt: int
    evidence: CandidateEvidence

    def __post_init__(self) -> None:
        _sha(self.plan_digest, "plan digest")
        if not isinstance(self.lane, LaneClass) or type(self.attempt) is not int or self.attempt < 0 or self.evidence.lane is not self.lane:
            raise M08ContractError("accepted entry identity is malformed")

    def as_dict(self) -> dict[str, Any]:
        return {"plan_digest": self.plan_digest, "lane": self.lane.value, "attempt": self.attempt, "evidence": self.evidence.as_dict()}


@dataclass(frozen=True, slots=True)
class AttemptRecord:
    lane: LaneClass
    attempt: int
    disposition: str
    candidate_id: str | None = None
    duplicate_of: str | None = None
    evidence: CandidateEvidence | None = None
    reason: str = ""
    plan_digest: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.lane, LaneClass) or type(self.attempt) is not int or self.attempt < 0 or self.disposition not in _ATTEMPT_DISPOSITIONS:
            raise M08ContractError("attempt record is malformed")
        if self.plan_digest is not None:
            _sha(self.plan_digest, "attempt plan digest")
        if self.disposition == "ACCEPT":
            if not self.evidence or self.candidate_id != self.evidence.candidate_id or self.duplicate_of is not None:
                raise M08ContractError("accepted attempt must carry its exact candidate evidence")
        elif self.evidence is not None or self.candidate_id is not None and self.disposition != "DUPLICATE":
            raise M08ContractError("non-accepted attempt carries accepted evidence")
        if self.disposition == "DUPLICATE" and (not self.candidate_id or not self.duplicate_of):
            raise M08ContractError("duplicate attempt must name both candidate and prior identity")

    def as_dict(self) -> dict[str, Any]:
        return {"lane": self.lane.value, "attempt": self.attempt, "disposition": self.disposition, "candidate_id": self.candidate_id, "duplicate_of": self.duplicate_of, "evidence": self.evidence.as_dict() if self.evidence else None, "reason": self.reason, "plan_digest": self.plan_digest}


@dataclass(frozen=True, slots=True)
class BatchResult:
    plan: BatchPlan
    entries: tuple[AcceptedBatchEntry, ...]
    attempted: Mapping[LaneClass, int]
    statistics: Mapping[str, int]
    status: str
    history_digest: str
    attempts: tuple[AttemptRecord, ...] = ()

    def __post_init__(self) -> None:
        if self.status not in {"COMPLETE", "PARTIAL", "EXHAUSTED", "UNAVAILABLE", "ERROR"}:
            raise M08ContractError("unknown terminal batch status")
        if any(entry.plan_digest != self.plan.digest() for entry in self.entries):
            raise M08ContractError("accepted entry is bound to another plan")
        ids = [entry.evidence.candidate_id for entry in self.entries]
        if len(ids) != len(set(ids)) or len({(entry.lane, entry.attempt) for entry in self.entries}) != len(self.entries):
            raise M08ContractError("accepted entries are duplicated")
        for key, value in self.statistics.items():
            if type(value) is not int or value < 0:
                raise M08ContractError(f"batch statistic {key} is malformed")
        expected_statistics = _stats(self.attempts)
        if dict(self.statistics) != expected_statistics:
            raise M08ContractError("batch statistics do not reconcile with immutable attempt history")
        expected_attempted = {request.lane: sum(item.lane is request.lane for item in self.attempts) for request in self.plan.cadence}
        if dict(self.attempted) != expected_attempted:
            raise M08ContractError("lane attempted counts do not reconcile with immutable attempt history")
        _sha(self.history_digest, "history digest")
        if self.attempts:
            accepted = {(item.lane, item.attempt): item for item in self.attempts if item.disposition == "ACCEPT"}
            expected = {(item.lane, item.attempt): item for item in self.entries}
            if set(accepted) != set(expected) or any(accepted[key].evidence != expected[key].evidence for key in expected):
                raise M08ContractError("attempt history and accepted entries disagree")

    def as_dict(self) -> dict[str, Any]:
        lanes = {request.lane.value: {"requested": request.requested_accepted, "attempted": int(self.attempted.get(request.lane, 0)), "accepted": sum(item.lane is request.lane for item in self.entries)} for request in self.plan.cadence}
        return {"schema": SCHEMA, "version": VERSION, "plan": self.plan.as_dict(), "plan_digest": self.plan.digest(), "lanes": lanes, "statistics": dict(sorted(self.statistics.items())), "attempts": [item.as_dict() for item in self.attempts], "accepted_entries": [item.as_dict() for item in sorted(self.entries, key=lambda item: (item.lane.value, item.attempt, item.evidence.candidate_id))], "status": self.status, "history_digest": self.history_digest}

    def digest(self) -> str:
        return digest(self.as_dict())

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "BatchResult":
        required = {"schema", "version", "plan", "plan_digest", "lanes", "statistics", "attempts", "accepted_entries", "status", "history_digest"}
        if set(value) != required or value.get("schema") != SCHEMA or value.get("version") != VERSION:
            raise M08ContractError("batch result schema is unsupported or incomplete")
        plan = BatchPlan.from_dict(value["plan"])
        if value["plan_digest"] != plan.digest() or not isinstance(value["attempts"], list) or not isinstance(value["accepted_entries"], list):
            raise M08ContractError("batch result plan/history binding is invalid")
        attempts: list[AttemptRecord] = []
        for item in value["attempts"]:
            if not isinstance(item, Mapping) or set(item) != {"lane", "attempt", "disposition", "candidate_id", "duplicate_of", "evidence", "reason", "plan_digest"}:
                raise M08ContractError("attempt history fields are unsupported or incomplete")
            evidence = CandidateEvidence.from_dict(item["evidence"]) if item["evidence"] is not None else None
            attempts.append(AttemptRecord(_lane(item["lane"]), item["attempt"], item["disposition"], item["candidate_id"], item["duplicate_of"], evidence, item["reason"], item["plan_digest"]))
        entries: list[AcceptedBatchEntry] = []
        for item in value["accepted_entries"]:
            if not isinstance(item, Mapping) or set(item) != {"plan_digest", "lane", "attempt", "evidence"}:
                raise M08ContractError("accepted entry fields are unsupported or incomplete")
            entries.append(AcceptedBatchEntry(item["plan_digest"], _lane(item["lane"]), item["attempt"], CandidateEvidence.from_dict(item["evidence"])))
        attempted = {_lane(key): item["attempted"] for key, item in value["lanes"].items()}
        result = cls(plan, tuple(entries), attempted, value["statistics"], value["status"], value["history_digest"], tuple(attempts))
        if result.as_dict() != dict(value):
            raise M08ContractError("batch result is not canonical or contains tampered fields")
        return result


def _normalize_history(plan: BatchPlan, history: Iterable[AcceptedBatchEntry | AttemptRecord]) -> list[AttemptRecord]:
    normalized: list[AttemptRecord] = []
    plan_digest = plan.digest()
    for item in history:
        if isinstance(item, AcceptedBatchEntry):
            if item.plan_digest != plan_digest:
                raise M08ContractError("resume history is bound to a different plan")
            normalized.append(AttemptRecord(item.lane, item.attempt, "ACCEPT", item.evidence.candidate_id, evidence=item.evidence, plan_digest=plan_digest))
        elif isinstance(item, AttemptRecord):
            if item.plan_digest is not None and item.plan_digest != plan_digest:
                raise M08ContractError("resume attempt is bound to a different plan")
            normalized.append(item)
        else:
            raise M08ContractError("resume history item is unsupported")
    seen: set[tuple[LaneClass, int]] = set()
    for item in normalized:
        key = (item.lane, item.attempt)
        if item.lane not in {request.lane for request in plan.cadence} or key in seen:
            raise M08ContractError("resume history has an unknown or duplicate attempt")
        budget = next(request.attempt_budget for request in plan.cadence if request.lane is item.lane)
        if item.attempt >= budget:
            raise M08ContractError("resume history exceeds its finite lane budget")
        seen.add(key)
    for request in plan.cadence:
        lane_attempts = sorted(item.attempt for item in normalized if item.lane is request.lane)
        if lane_attempts != list(range(len(lane_attempts))):
            raise M08ContractError("resume history is not a contiguous deterministic prefix")
    return sorted(normalized, key=lambda item: (next(index for index, request in enumerate(plan.cadence) if request.lane is item.lane), item.attempt))


def _stats(attempts: Iterable[AttemptRecord]) -> dict[str, int]:
    records = list(attempts)
    return {"generated": len(records), "accepted": sum(item.disposition == "ACCEPT" for item in records), "rejected": sum(item.disposition == "REJECT" for item in records), "duplicate": sum(item.disposition == "DUPLICATE" for item in records), "unavailable": sum(item.disposition == "UNAVAILABLE" for item in records), "inconclusive": sum(item.disposition == "INCONCLUSIVE" for item in records), "error": sum(item.disposition == "ERROR" for item in records)}


def run_batch(plan: BatchPlan, producer: Callable[[LaneClass, int, int], Mapping[str, Any] | None], *, history: Iterable[AcceptedBatchEntry | AttemptRecord] = (), max_total_attempts: int | None = None) -> BatchResult:
    """Run a finite ordered cadence over existing generation/validation authority."""
    attempts = _normalize_history(plan, history)
    seen = {item.candidate_id for item in attempts if item.disposition == "ACCEPT"}
    if max_total_attempts is not None and (type(max_total_attempts) is not int or max_total_attempts < 0):
        raise M08ContractError("overall attempt budget is malformed")
    for request in plan.cadence:
        accepted = sum(item.disposition == "ACCEPT" and item.lane is request.lane for item in attempts)
        next_attempt = sum(item.lane is request.lane for item in attempts)
        if accepted >= request.requested_accepted:
            continue
        for ordinal in range(next_attempt, request.attempt_budget):
            if accepted >= request.requested_accepted or (max_total_attempts is not None and len(attempts) >= max_total_attempts):
                break
            try:
                raw = producer(request.lane, ordinal, plan.root_seed)
            except Exception as exc:  # producer failures are terminal evidence, never hidden retries
                attempts.append(AttemptRecord(request.lane, ordinal, "ERROR", reason=type(exc).__name__, plan_digest=plan.digest()))
                continue
            if raw is None or raw.get("disposition") == "UNAVAILABLE":
                attempts.append(AttemptRecord(request.lane, ordinal, "UNAVAILABLE", reason="evidence unavailable", plan_digest=plan.digest()))
                continue
            disposition = str(raw.get("disposition", "REJECT"))
            if disposition in {"INCONCLUSIVE", "REJECT"}:
                attempts.append(AttemptRecord(request.lane, ordinal, disposition, reason=str(raw.get("reason", "")), plan_digest=plan.digest()))
                continue
            if disposition != "ACCEPT":
                attempts.append(AttemptRecord(request.lane, ordinal, "ERROR", reason="unsupported producer disposition", plan_digest=plan.digest()))
                continue
            evidence = raw.get("evidence")
            if not isinstance(evidence, CandidateEvidence) or evidence.lane is not request.lane:
                attempts.append(AttemptRecord(request.lane, ordinal, "REJECT", reason="M04 lane/evidence mismatch", plan_digest=plan.digest()))
                continue
            if evidence.candidate_id in seen:
                attempts.append(AttemptRecord(request.lane, ordinal, "DUPLICATE", evidence.candidate_id, evidence.candidate_id, reason="candidate identity already accepted", plan_digest=plan.digest()))
                continue
            attempts.append(AttemptRecord(request.lane, ordinal, "ACCEPT", evidence.candidate_id, evidence=evidence, plan_digest=plan.digest()))
            seen.add(evidence.candidate_id)
            accepted += 1
    entries = tuple(AcceptedBatchEntry(plan.digest(), item.lane, item.attempt, item.evidence) for item in attempts if item.disposition == "ACCEPT" and item.evidence is not None)
    attempted = {request.lane: sum(item.lane is request.lane for item in attempts) for request in plan.cadence}
    statistics = _stats(attempts)
    complete = all(sum(item.lane is request.lane and item.disposition == "ACCEPT" for item in attempts) >= request.requested_accepted for request in plan.cadence)
    budgets_exhausted = all(attempted[request.lane] >= request.attempt_budget for request in plan.cadence)
    interrupted = max_total_attempts is not None and len(attempts) >= max_total_attempts and not budgets_exhausted and not complete
    unavailable = bool(attempts) and all(item.disposition in {"UNAVAILABLE", "INCONCLUSIVE"} for item in attempts) and not complete
    status = "COMPLETE" if complete else "UNAVAILABLE" if unavailable else "PARTIAL" if interrupted else "EXHAUSTED" if budgets_exhausted else "PARTIAL"
    history_digest = digest({"plan_digest": plan.digest(), "attempts": [item.as_dict() for item in attempts], "statistics": statistics})
    return BatchResult(plan, entries, attempted, statistics, status, history_digest, tuple(attempts))


def verify_artifact_set(evidence: CandidateEvidence, artifacts: Mapping[str, bytes]) -> dict[str, Any]:
    """Verify canonical immutable bytes referenced by one accepted entry.

    The batch contract stores references and digests; this helper is the
    boundary check used before materializing a result manifest.  It never
    regenerates or re-encodes an artifact and ignores no required identity.
    """
    required = (
        (evidence.level_data_ref, evidence.level_data_digest),
        (evidence.logical_art_ref, evidence.logical_art_digest),
        (evidence.bundle_ref, evidence.bundle_digest),
        (evidence.source_provenance_ref, evidence.source_provenance_digest),
        (evidence.m03_ref, evidence.m03_digest),
        (evidence.m04_ref, evidence.m04_digest),
        (evidence.m05_ref, evidence.m05_digest),
        (evidence.generation_ref, evidence.generation_metadata_digest),
    )
    optional = ((evidence.preview_ref, evidence.preview_digest), (evidence.mutation_ref, evidence.mutation_digest))
    verified: list[str] = []
    for reference, expected in (*required, *optional):
        if reference is None:
            continue
        value = artifacts.get(reference)
        if not isinstance(value, bytes) or expected is None or hashlib.sha256(value).hexdigest() != expected:
            raise M08ContractError(f"artifact bytes are missing or stale for {reference}")
        verified.append(reference)
    return {"disposition": "ACCEPT", "verified_references": tuple(sorted(verified)), "artifact_set_digest": digest({"references": sorted(verified), "digests": sorted((reference, hashlib.sha256(artifacts[reference]).hexdigest()) for reference in verified)})}


def _review_chain(result: BatchResult, evidence: CandidateEvidence, reviews: Iterable[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    candidate_reviews = [dict(review) for review in reviews if isinstance(review, Mapping) and review.get("candidate_id") == evidence.candidate_id]
    valid: list[dict[str, Any]] = []
    invalid: list[str] = []
    seen_review_ids: set[str] = set()
    for review in candidate_reviews:
        review_id = str(review.get("review_id", f"review-{len(valid) + 1}"))
        if review_id in seen_review_ids:
            invalid.append(review_id)
            continue
        seen_review_ids.add(review_id)
        if review.get("disposition") not in {"ACCEPT", "REJECT"} or review.get("artwork_sha256", evidence.logical_art_digest) != evidence.logical_art_digest:
            invalid.append(review_id)
            continue
        sequence = review.get("sequence")
        if sequence is not None and (type(sequence) is not int or sequence < 1):
            invalid.append(review_id)
            continue
        valid.append(review)
    if any(item.get("sequence") is not None for item in valid):
        ordered = sorted(valid, key=lambda item: item.get("sequence", 0))
        previous: str | None = None
        contiguous: list[dict[str, Any]] = []
        for expected, review in enumerate(ordered, 1):
            if review.get("sequence") != expected or review.get("previous_review_id") != previous:
                invalid.append(str(review.get("review_id", "unknown")))
                break
            contiguous.append(review)
            previous = str(review.get("review_id"))
        valid = contiguous
    else:
        # Test/durable adapters without sequence numbers still have a stable
        # derived view; canonical SB-LFX records use sequence and predecessor.
        valid.sort(key=lambda item: str(item.get("review_id", "")))
    return valid, invalid


def review_summary(result: BatchResult, reviews: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    all_reviews = list(reviews)
    states: dict[str, str] = {}
    invalid: dict[str, list[str]] = {}
    for entry in result.entries:
        chain, bad = _review_chain(result, entry.evidence, all_reviews)
        candidate_id = entry.evidence.candidate_id
        states[candidate_id] = "OWNER_ACCEPTED" if chain and chain[-1]["disposition"] == "ACCEPT" else "OWNER_REJECTED" if chain and chain[-1]["disposition"] == "REJECT" else "NEEDS_REVIEW"
        if bad:
            invalid[candidate_id] = sorted(bad)
    return {"NEEDS_REVIEW": sum(value == "NEEDS_REVIEW" for value in states.values()), "OWNER_ACCEPTED": sum(value == "OWNER_ACCEPTED" for value in states.values()), "OWNER_REJECTED": sum(value == "OWNER_REJECTED" for value in states.values()), "INVALID_REVIEW_EVIDENCE": len(invalid), "invalid_review_evidence": invalid, "states": dict(sorted(states.items()))}


def build_handoff(result: BatchResult, candidate_id: str, reviews: Iterable[Mapping[str, Any]], *, artifacts: Mapping[str, bytes] | None = None) -> dict[str, Any]:
    entry = next((item for item in result.entries if item.evidence.candidate_id == candidate_id), None)
    if entry is None:
        return {"schema": HANDOFF_SCHEMA, "version": HANDOFF_VERSION, "disposition": "NOT_FACTORY_ACCEPTED", "candidate_id": candidate_id}
    chain, invalid = _review_chain(result, entry.evidence, reviews)
    if invalid or not chain or chain[-1]["disposition"] != "ACCEPT":
        return {"schema": HANDOFF_SCHEMA, "version": HANDOFF_VERSION, "disposition": "NOT_OWNER_ACCEPTED", "candidate_id": candidate_id, "batch_result_digest": result.digest()}
    if artifacts is None:
        return {"schema": HANDOFF_SCHEMA, "version": HANDOFF_VERSION, "disposition": "UNAVAILABLE", "candidate_id": candidate_id, "batch_result_digest": result.digest(), "reason": "immutable artifact bytes were not supplied for digest verification"}
    try:
        artifact_check = verify_artifact_set(entry.evidence, artifacts)
    except M08ContractError as exc:
        return {"schema": HANDOFF_SCHEMA, "version": HANDOFF_VERSION, "disposition": "ERROR", "candidate_id": candidate_id, "batch_result_digest": result.digest(), "reason": str(exc)}
    payload: dict[str, Any] = {"schema": HANDOFF_SCHEMA, "version": HANDOFF_VERSION, "disposition": "READY", "batch_result_digest": result.digest(), "plan_digest": result.plan.digest(), "candidate": entry.as_dict(), "owner_review_chain": chain, "owner_review_chain_digest": digest({"chain": chain}), "artifact_set_digest": artifact_check["artifact_set_digest"]}
    payload["handoff_digest"] = digest(payload)
    return payload


__all__ = ["AcceptedBatchEntry", "AttemptRecord", "BatchPlan", "BatchResult", "CandidateEvidence", "HANDOFF_SCHEMA", "LaneRequest", "M08ContractError", "POLICY_VERSION", "SCHEMA", "build_handoff", "digest", "review_summary", "run_batch", "verify_artifact_set"]
