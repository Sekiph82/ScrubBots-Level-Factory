"""Offline, deterministic M08 production batch contracts.

This module is an evidence envelope around existing generators and validators;
it deliberately does not compile levels, solve puzzles, render art, or create
a second review store.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import PurePosixPath
from typing import Any, Callable, Iterable, Mapping, Sequence

from .difficulty_analysis import LaneClass

SCHEMA = "scrubbots-m08-production-batch"
VERSION = 1
ARTIFACT_SCHEMA = "scrubbots-m08-accepted-batch-result"
HANDOFF_SCHEMA = "scrubbots-m08-content-pipeline-handoff"
POLICY_VERSION = "M08_FACTORY_ACCEPTANCE_V1"
_DISPOSITIONS = {"ACCEPT", "REJECT", "INCONCLUSIVE", "UNAVAILABLE", "ERROR"}


class M08ContractError(ValueError):
    pass


def _bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Mapping[str, Any] | bytes | str) -> str:
    if isinstance(value, Mapping):
        value = _bytes(value)
    elif isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _sha(value: Any, label: str) -> str:
    if type(value) is not str or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise M08ContractError(f"{label} must be a lowercase SHA-256")
    return value


def _safe_ref(value: str, label: str) -> str:
    if type(value) is not str or not value or value.startswith("/") or ":" in value or "\\" in value:
        raise M08ContractError(f"{label} must be a safe portable relative path")
    p = PurePosixPath(value)
    if ".." in p.parts or p.is_absolute():
        raise M08ContractError(f"{label} may not traverse directories")
    return value


@dataclass(frozen=True, slots=True)
class LaneRequest:
    lane: LaneClass
    requested_accepted: int
    attempt_budget: int

    def __post_init__(self) -> None:
        if not isinstance(self.lane, LaneClass) or type(self.requested_accepted) is not int or self.requested_accepted < 0 or type(self.attempt_budget) is not int or self.attempt_budget < 1:
            raise M08ContractError("lane request is malformed")
        if self.requested_accepted > self.attempt_budget:
            raise M08ContractError("requested accepted count exceeds finite lane budget")

    def as_dict(self) -> dict[str, Any]:
        return {"lane": self.lane.value, "requested_accepted": self.requested_accepted, "attempt_budget": self.attempt_budget}


@dataclass(frozen=True, slots=True)
class BatchPlan:
    cadence: tuple[LaneRequest, ...]
    root_seed: int
    seed_namespace: str
    generation_policy: str = POLICY_VERSION
    m04_lane_policy: str = "SCORE_LANE_V1"
    schema: str = SCHEMA
    version: int = VERSION

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.version != VERSION or not self.cadence or len({x.lane for x in self.cadence}) != len(self.cadence):
            raise M08ContractError("plan schema/cadence is malformed")
        if type(self.root_seed) is not int or not isinstance(self.seed_namespace, str) or not self.seed_namespace.strip():
            raise M08ContractError("plan seed identity is malformed")
        if not self.generation_policy.strip() or not self.m04_lane_policy.strip():
            raise M08ContractError("plan policy identity is required")

    def as_dict(self) -> dict[str, Any]:
        return {"schema": self.schema, "version": self.version, "cadence": [x.as_dict() for x in self.cadence], "root_seed": self.root_seed, "seed_namespace": self.seed_namespace, "generation_policy": self.generation_policy, "m04_lane_policy": self.m04_lane_policy}

    def digest(self) -> str:
        return digest(self.as_dict())


@dataclass(frozen=True, slots=True)
class CandidateEvidence:
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
    bundle_digest: str
    preview_digest: str | None = None
    mutation_digest: str | None = None
    references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.candidate_id.strip() or not isinstance(self.lane, LaneClass):
            raise M08ContractError("candidate identity/lane is malformed")
        for value, label in ((self.m03_digest, "M03"), (self.m04_digest, "M04"), (self.m04_lane_digest, "M04 lane"), (self.m05_digest, "M05"), (self.level_data_digest, "LevelData"), (self.logical_art_digest, "logical art"), (self.source_provenance_digest, "source"), (self.generation_request_digest, "generation request"), (self.generation_result_digest, "generation result"), (self.bundle_digest, "bundle")):
            _sha(value, label)
        for value, label in ((self.preview_digest, "preview"), (self.mutation_digest, "mutation")):
            if value is not None:
                _sha(value, label)
        if self.m03_disposition != "ACCEPT" or self.m04_disposition != "ACCEPT" or self.m05_disposition != "ACCEPT":
            raise M08ContractError("only exact M03/M04/M05 ACCEPT evidence can form a factory-accepted candidate")
        for ref in self.references:
            _safe_ref(ref, "artifact reference")

    def as_dict(self) -> dict[str, Any]:
        return {"candidate_id": self.candidate_id, "lane": self.lane.value, "m03_disposition": self.m03_disposition, "m03_digest": self.m03_digest, "m04_disposition": self.m04_disposition, "m04_digest": self.m04_digest, "m04_lane_digest": self.m04_lane_digest, "m05_disposition": self.m05_disposition, "m05_digest": self.m05_digest, "level_data_digest": self.level_data_digest, "logical_art_digest": self.logical_art_digest, "source_provenance_digest": self.source_provenance_digest, "generation_request_digest": self.generation_request_digest, "generation_result_digest": self.generation_result_digest, "bundle_digest": self.bundle_digest, "preview_digest": self.preview_digest, "mutation_digest": self.mutation_digest, "references": list(self.references)}


@dataclass(frozen=True, slots=True)
class AcceptedBatchEntry:
    plan_digest: str
    lane: LaneClass
    attempt: int
    evidence: CandidateEvidence

    def __post_init__(self) -> None:
        _sha(self.plan_digest, "plan digest")
        if type(self.attempt) is not int or self.attempt < 0 or self.evidence.lane is not self.lane:
            raise M08ContractError("accepted entry identity is malformed")

    def as_dict(self) -> dict[str, Any]:
        return {"plan_digest": self.plan_digest, "lane": self.lane.value, "attempt": self.attempt, "evidence": self.evidence.as_dict()}


@dataclass(frozen=True, slots=True)
class BatchResult:
    plan: BatchPlan
    entries: tuple[AcceptedBatchEntry, ...]
    attempted: Mapping[LaneClass, int]
    statistics: Mapping[str, int]
    status: str
    history_digest: str

    def __post_init__(self) -> None:
        if self.status not in {"COMPLETE", "PARTIAL", "EXHAUSTED", "UNAVAILABLE", "ERROR"}:
            raise M08ContractError("unknown terminal batch status")
        ids = [x.evidence.candidate_id for x in self.entries]
        if len(ids) != len(set(ids)) or any(x.plan_digest != self.plan.digest() for x in self.entries):
            raise M08ContractError("accepted entries are duplicated or bound to another plan")
        if any(type(v) is not int or v < 0 for v in self.statistics.values()):
            raise M08ContractError("batch statistics are malformed")
        _sha(self.history_digest, "history digest")

    def as_dict(self) -> dict[str, Any]:
        lanes = {request.lane.value: {"attempted": int(self.attempted.get(request.lane, 0)), "accepted": sum(x.lane is request.lane for x in self.entries), "requested": request.requested_accepted} for request in self.plan.cadence}
        return {"schema": SCHEMA, "version": VERSION, "plan": self.plan.as_dict(), "plan_digest": self.plan.digest(), "lanes": lanes, "statistics": dict(sorted(self.statistics.items())), "accepted_entries": [x.as_dict() for x in sorted(self.entries, key=lambda x: (x.lane.value, x.attempt, x.evidence.candidate_id))], "status": self.status, "history_digest": self.history_digest}

    def digest(self) -> str:
        return digest(self.as_dict())


def run_batch(plan: BatchPlan, producer: Callable[[LaneClass, int, int], Mapping[str, Any] | None], *, history: Iterable[AcceptedBatchEntry] = (), max_total_attempts: int | None = None) -> BatchResult:
    """Run a finite deterministic cadence over an existing producer/validator."""
    prior = tuple(history)
    if any(entry.plan_digest != plan.digest() for entry in prior):
        raise M08ContractError("resume history is bound to a different plan")
    entries = list(prior)
    seen = {x.evidence.candidate_id for x in entries}
    attempted = {request.lane: max((x.attempt for x in prior if x.lane is request.lane), default=-1) + 1 for request in plan.cadence}
    stats = {"generated": sum(attempted.values()), "rejected": 0, "duplicate": 0, "unavailable": 0, "inconclusive": 0, "accepted": len(entries)}
    total = 0
    for request in plan.cadence:
        already = sum(x.lane is request.lane for x in entries)
        for ordinal in range(request.attempt_budget):
            if already >= request.requested_accepted:
                break
            if max_total_attempts is not None and total >= max_total_attempts:
                break
            total += 1; attempted[request.lane] += 1; stats["generated"] += 1
            raw = producer(request.lane, ordinal, plan.root_seed)
            if raw is None:
                stats["unavailable"] += 1; continue
            disposition = str(raw.get("disposition", "REJECT"))
            if disposition in {"UNAVAILABLE", "INCONCLUSIVE"}:
                stats[disposition.casefold()] += 1; continue
            if disposition != "ACCEPT":
                stats["rejected"] += 1; continue
            try:
                evidence = raw["evidence"]
                if not isinstance(evidence, CandidateEvidence) or evidence.lane is not request.lane:
                    stats["rejected"] += 1; continue
                if evidence.candidate_id in seen:
                    stats["duplicate"] += 1; continue
                entries.append(AcceptedBatchEntry(plan.digest(), request.lane, ordinal, evidence)); seen.add(evidence.candidate_id); already += 1; stats["accepted"] += 1
            except (KeyError, M08ContractError):
                stats["rejected"] += 1
    complete = all(sum(x.lane is r.lane for x in entries) >= r.requested_accepted for r in plan.cadence)
    status = "COMPLETE" if complete else "EXHAUSTED"
    history_digest = digest({"plan_digest": plan.digest(), "entries": [x.as_dict() for x in sorted(entries, key=lambda x: (x.lane.value, x.attempt, x.evidence.candidate_id))], "attempted": {k.value: v for k, v in attempted.items()}, "statistics": stats})
    return BatchResult(plan, tuple(entries), attempted, stats, status, history_digest)


def review_summary(result: BatchResult, reviews: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    valid: dict[str, Mapping[str, Any]] = {}
    for review in reviews:
        candidate_id = str(review.get("candidate_id", ""))
        if candidate_id not in {x.evidence.candidate_id for x in result.entries} or review.get("disposition") not in {"ACCEPT", "REJECT"}:
            continue
        valid[candidate_id] = review
    states = {x.evidence.candidate_id: "NEEDS_REVIEW" for x in result.entries}
    for cid, review in valid.items():
        states[cid] = "OWNER_ACCEPTED" if review["disposition"] == "ACCEPT" else "OWNER_REJECTED"
    return {"NEEDS_REVIEW": sum(v == "NEEDS_REVIEW" for v in states.values()), "OWNER_ACCEPTED": sum(v == "OWNER_ACCEPTED" for v in states.values()), "OWNER_REJECTED": sum(v == "OWNER_REJECTED" for v in states.values()), "states": dict(sorted(states.items()))}


def build_handoff(result: BatchResult, candidate_id: str, reviews: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    entry = next((x for x in result.entries if x.evidence.candidate_id == candidate_id), None)
    if entry is None:
        return {"schema": HANDOFF_SCHEMA, "version": VERSION, "disposition": "NOT_FACTORY_ACCEPTED", "candidate_id": candidate_id}
    review = [x for x in reviews if x.get("candidate_id") == candidate_id and x.get("disposition") == "ACCEPT"]
    if not review:
        return {"schema": HANDOFF_SCHEMA, "version": VERSION, "disposition": "NOT_OWNER_ACCEPTED", "candidate_id": candidate_id, "batch_result_digest": result.digest()}
    payload = {"schema": HANDOFF_SCHEMA, "version": VERSION, "disposition": "READY", "batch_result_digest": result.digest(), "candidate": entry.as_dict(), "owner_review": review[-1]}
    payload["handoff_digest"] = digest(payload)
    return payload


__all__ = ["AcceptedBatchEntry", "BatchPlan", "BatchResult", "CandidateEvidence", "HANDOFF_SCHEMA", "LaneRequest", "M08ContractError", "POLICY_VERSION", "SCHEMA", "build_handoff", "digest", "review_summary", "run_batch"]
