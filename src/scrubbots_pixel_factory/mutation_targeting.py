"""SB-LF07-006 typed targeting service over authentic producer adapters."""

from collections.abc import Sequence
from dataclasses import dataclass
import hashlib
import json
import math

from .m07_services import MutationContractError, TargetDisposition, TargetSelection, TypedChallengeTarget, SafetyConstraintEvidence, ValidationEnvelope, ValidationDisposition
from .difficulty_analysis import CHALLENGE_SCORE_POLICY_VERSION, CHALLENGE_SCORE_SCHEMA, CHALLENGE_SCORE_VERSION
from .mutation_evidence import AuthenticEvidenceAdapter


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def _challenge_score_policy_digest(policy_version: str) -> str:
    if policy_version != CHALLENGE_SCORE_POLICY_VERSION:
        raise MutationContractError("unsupported accepted Challenge Score policy identity")
    return _digest({"schema": CHALLENGE_SCORE_SCHEMA, "version": CHALLENGE_SCORE_VERSION, "policy_version": policy_version})


@dataclass(frozen=True, slots=True)
class AuthenticTargetCandidate:
    envelope: ValidationEnvelope
    solver: AuthenticEvidenceAdapter
    difficulty: AuthenticEvidenceAdapter
    qa: AuthenticEvidenceAdapter

    def __post_init__(self) -> None:
        if self.solver.stage != "M03_SOLVER" or self.difficulty.stage != "M04_DIFFICULTY" or self.qa.stage != "M05_QA":
            raise MutationContractError("target candidate requires authentic M03/M04/M05 adapters")
        if (self.envelope.solver.canonical_dict() != self.solver.record.canonical_dict() or self.envelope.difficulty.canonical_dict() != self.difficulty.record.canonical_dict() or self.envelope.qa.canonical_dict() != self.qa.record.canonical_dict()):
            raise MutationContractError("target candidate evidence is not the exact authenticated envelope evidence")


def build_typed_target(minimum: float, maximum: float, difficulty: AuthenticEvidenceAdapter, qa: AuthenticEvidenceAdapter) -> TypedChallengeTarget:
    if difficulty.stage != "M04_DIFFICULTY" or qa.stage != "M05_QA":
        raise MutationContractError("typed target requires authentic M04/M05 adapters")
    score = difficulty.record.payload.get("challenge_score")
    policy = difficulty.record.payload.get("policy_version")
    if type(score) not in (int, float) or not math.isfinite(float(score)) or type(policy) is not str:
        raise MutationContractError("accepted M04 Challenge Score/policy evidence is unavailable")
    policy_digest = _challenge_score_policy_digest(policy)
    # No accepted repository producer currently supplies load, risk, or retention
    # truth. A generic M05 ACCEPT is structural QA, not these constraints.
    safety = SafetyConstraintEvidence("scrubbots-m07-safety-availability", "UNAVAILABLE", policy_digest, False, False, False, "0" * 64)
    return TypedChallengeTarget(minimum, maximum, policy_digest, safety)


def select_authentic_target(target: TypedChallengeTarget, candidates: Sequence[AuthenticTargetCandidate]) -> TargetSelection:
    if not isinstance(target, TypedChallengeTarget):
        raise MutationContractError("typed target is required")
    matches: list[ValidationEnvelope] = []
    saw_unavailable = False
    saw_inconclusive = False
    for item in candidates:
        if item.difficulty.record.payload.get("policy_version") is None or item.difficulty.record.payload.get("challenge_score") is None:
            saw_inconclusive = True
            continue
        if item.qa.producer is None:
            saw_unavailable = True
            continue
        if item.envelope.disposition is not ValidationDisposition.ELIGIBLE:
            saw_inconclusive = True
            continue
        score = item.envelope.challenge_score
        candidate_policy = _challenge_score_policy_digest(item.difficulty.record.payload.get("policy_version")) if type(item.difficulty.record.payload.get("policy_version")) is str else None
        if candidate_policy != target.policy_digest or not target.safety.load_ok or not target.safety.risk_ok or not target.safety.retention_ok or score is None:
            saw_inconclusive = True
            continue
        if target.minimum <= score <= target.maximum:
            matches.append(item.envelope)
    if matches:
        midpoint = (target.minimum + target.maximum) / 2.0
        selected = min(matches, key=lambda item: (abs(float(item.challenge_score) - midpoint), item.child.state_digest, item.mutation_digest))
        reason = "deterministic authenticated score-distance then child-digest selection"
        return TargetSelection(TargetDisposition.MATCH, target.digest(), selected, reason, _digest({"target": target.digest(), "selected": selected.canonical_dict(), "reason": reason}))
    disposition = TargetDisposition.UNAVAILABLE if saw_unavailable and not saw_inconclusive else TargetDisposition.INCONCLUSIVE if saw_inconclusive else TargetDisposition.NO_MATCH
    reason = "authentic safety/evidence capability is unavailable" if disposition is TargetDisposition.UNAVAILABLE else "no complete authenticated target candidate matched" if disposition is TargetDisposition.INCONCLUSIVE else "no authenticated candidate fell inside the requested range"
    return TargetSelection(disposition, target.digest(), None, reason, _digest({"target": target.digest(), "selected": None, "reason": reason}))


__all__ = ["AuthenticTargetCandidate", "build_typed_target", "select_authentic_target"]
