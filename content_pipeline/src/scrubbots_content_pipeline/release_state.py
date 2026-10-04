"""Deterministic, append-only in-memory publish/promotion/rollback ledger."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from enum import StrEnum
from collections.abc import Sequence

from .config import Environment

RELEASE_STATE_VERSION = "1.0"
_GENESIS_DIGEST = "0" * 64
_DIGEST_SIZE = 64


class ReleaseState(StrEnum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    STAGED = "STAGED"
    PROMOTION_PENDING = "PROMOTION_PENDING"
    PRODUCTION_PROMOTED = "PRODUCTION_PROMOTED"
    ROLLED_BACK = "ROLLED_BACK"
    SUPERSEDED = "SUPERSEDED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"


class ReleaseReasonCode(StrEnum):
    VALID_TRANSITION = "VALID_TRANSITION"
    INVALID_EVENT = "INVALID_EVENT"
    DUPLICATE_EVENT_ID = "DUPLICATE_EVENT_ID"
    DUPLICATE_TRANSITION_ID = "DUPLICATE_TRANSITION_ID"
    INVALID_SEQUENCE = "INVALID_SEQUENCE"
    EVENT_CHAIN_MISMATCH = "EVENT_CHAIN_MISMATCH"
    EVENT_DIGEST_MISMATCH = "EVENT_DIGEST_MISMATCH"
    STALE_EXPECTED_STATE = "STALE_EXPECTED_STATE"
    ILLEGAL_TRANSITION = "ILLEGAL_TRANSITION"
    ENVIRONMENT_MISMATCH = "ENVIRONMENT_MISMATCH"
    PROMOTION_REQUIRED = "PROMOTION_REQUIRED"
    INVALID_PROMOTION_SOURCE = "INVALID_PROMOTION_SOURCE"
    UNKNOWN_ROLLBACK_TARGET = "UNKNOWN_ROLLBACK_TARGET"


@dataclass(frozen=True, slots=True)
class ReleaseEvent:
    event_version: str
    sequence: int
    event_id: str
    transition_id: str
    record_id: str
    content_id: str
    content_digest: str
    environment: Environment
    from_state: ReleaseState | None
    to_state: ReleaseState
    expected_state: ReleaseState | None
    previous_event_digest: str
    promotion_intent: bool = False
    source_record_id: str | None = None
    rollback_to_record_id: str | None = None
    rollback_to_content_id: str | None = None
    rollback_to_digest: str | None = None
    event_digest: str = ""


@dataclass(frozen=True, slots=True)
class ReleaseStateSnapshot:
    record_version: str
    record_id: str
    content_id: str
    content_digest: str
    environment: Environment
    state: ReleaseState
    last_sequence: int

    def to_dict(self) -> dict[str, object]:
        return {
            "record_version": self.record_version,
            "record_id": self.record_id,
            "content_id": self.content_id,
            "content_digest": self.content_digest,
            "environment": self.environment.value,
            "state": self.state.value,
            "last_sequence": self.last_sequence,
        }


@dataclass(frozen=True, slots=True)
class ReleaseTransitionResult:
    result_version: str
    accepted: bool
    reason_code: ReleaseReasonCode
    event_sequence: int | None
    current_record_id: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "result_version": self.result_version,
            "accepted": self.accepted,
            "reason_code": self.reason_code.value,
            "event_sequence": self.event_sequence,
            "current_record_id": self.current_record_id,
        }


@dataclass(frozen=True, slots=True)
class ReleaseReplayResult:
    accepted: bool
    reason_code: ReleaseReasonCode
    snapshots: tuple[ReleaseStateSnapshot, ...]
    current_production_record_id: str | None
    transition_result: ReleaseTransitionResult


def _event_payload(event: ReleaseEvent) -> dict[str, object]:
    return {
        "event_version": event.event_version,
        "sequence": event.sequence,
        "event_id": event.event_id,
        "transition_id": event.transition_id,
        "record_id": event.record_id,
        "content_id": event.content_id,
        "content_digest": event.content_digest,
        "environment": event.environment.value if isinstance(event.environment, Environment) else str(event.environment),
        "from_state": event.from_state.value if isinstance(event.from_state, ReleaseState) else None,
        "to_state": event.to_state.value if isinstance(event.to_state, ReleaseState) else str(event.to_state),
        "expected_state": event.expected_state.value if isinstance(event.expected_state, ReleaseState) else None,
        "previous_event_digest": event.previous_event_digest,
        "promotion_intent": event.promotion_intent,
        "source_record_id": event.source_record_id,
        "rollback_to_record_id": event.rollback_to_record_id,
        "rollback_to_content_id": event.rollback_to_content_id,
        "rollback_to_digest": event.rollback_to_digest,
    }


def _canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def make_release_event(
    *, sequence: int, event_id: str, transition_id: str, record_id: str,
    content_id: str, content_digest: str, environment: Environment,
    from_state: ReleaseState | None, to_state: ReleaseState,
    expected_state: ReleaseState | None, previous_event_digest: str,
    promotion_intent: bool = False, source_record_id: str | None = None,
    rollback_to_record_id: str | None = None, rollback_to_content_id: str | None = None,
    rollback_to_digest: str | None = None,
) -> ReleaseEvent:
    """Create a content-addressed event from explicit IDs and sequence inputs."""
    event = ReleaseEvent(
        event_version=RELEASE_STATE_VERSION, sequence=sequence, event_id=event_id,
        transition_id=transition_id, record_id=record_id, content_id=content_id,
        content_digest=content_digest, environment=environment, from_state=from_state,
        to_state=to_state, expected_state=expected_state,
        previous_event_digest=previous_event_digest, promotion_intent=promotion_intent,
        source_record_id=source_record_id, rollback_to_record_id=rollback_to_record_id,
        rollback_to_content_id=rollback_to_content_id, rollback_to_digest=rollback_to_digest,
    )
    digest = hashlib.sha256(_canonical(_event_payload(event)).encode("utf-8")).hexdigest()
    return replace(event, event_digest=digest)


def serialize_release_event(event: ReleaseEvent) -> str:
    return _canonical({**_event_payload(event), "event_digest": event.event_digest})


def serialize_release_snapshot(snapshot: ReleaseStateSnapshot) -> str:
    return _canonical(snapshot.to_dict())


def serialize_transition_result(result: ReleaseTransitionResult) -> str:
    return _canonical(result.to_dict())


def _valid_event(event: object) -> bool:
    if not isinstance(event, ReleaseEvent):
        return False
    if event.event_version != RELEASE_STATE_VERSION or type(event.sequence) is not int or event.sequence < 1:
        return False
    if not all(isinstance(value, str) and value for value in (event.event_id, event.transition_id, event.record_id, event.content_id)):
        return False
    if not isinstance(event.environment, Environment) or not isinstance(event.to_state, ReleaseState):
        return False
    if event.from_state is not None and not isinstance(event.from_state, ReleaseState):
        return False
    if event.expected_state is not None and not isinstance(event.expected_state, ReleaseState):
        return False
    if not isinstance(event.content_digest, str) or len(event.content_digest) != _DIGEST_SIZE or any(char not in "0123456789abcdef" for char in event.content_digest):
        return False
    if not isinstance(event.previous_event_digest, str) or len(event.previous_event_digest) != _DIGEST_SIZE:
        return False
    if type(event.promotion_intent) is not bool:
        return False
    expected_digest = hashlib.sha256(_canonical(_event_payload(event)).encode("utf-8")).hexdigest()
    return event.event_digest == expected_digest


def _result(accepted: bool, reason: ReleaseReasonCode, event: ReleaseEvent | None, current: str | None) -> ReleaseTransitionResult:
    return ReleaseTransitionResult(RELEASE_STATE_VERSION, accepted, reason, event.sequence if event else None, current)


def replay_release_events(events: Sequence[ReleaseEvent]) -> ReleaseReplayResult:
    """Replay and verify the complete immutable hash-chained event sequence."""
    records: dict[str, ReleaseStateSnapshot] = {}
    seen_events: set[str] = set()
    seen_transitions: set[str] = set()
    current_production: str | None = None
    previous_digest = _GENESIS_DIGEST

    def reject(reason: ReleaseReasonCode, event: ReleaseEvent | None) -> ReleaseReplayResult:
        current = _result(False, reason, event, current_production)
        return ReleaseReplayResult(False, reason, tuple(records[key] for key in sorted(records)), current_production, current)

    for expected_sequence, event in enumerate(events, start=1):
        if not isinstance(event, ReleaseEvent):
            return reject(ReleaseReasonCode.INVALID_EVENT, None)
        if event.event_id in seen_events:
            return reject(ReleaseReasonCode.DUPLICATE_EVENT_ID, event)
        if event.transition_id in seen_transitions:
            return reject(ReleaseReasonCode.DUPLICATE_TRANSITION_ID, event)
        if event.sequence != expected_sequence:
            return reject(ReleaseReasonCode.INVALID_SEQUENCE, event)
        if event.previous_event_digest != previous_digest:
            return reject(ReleaseReasonCode.EVENT_CHAIN_MISMATCH, event)
        if not _valid_event(event):
            return reject(ReleaseReasonCode.EVENT_DIGEST_MISMATCH, event)

        existing = records.get(event.record_id)
        if existing is None:
            if event.from_state is not None or event.expected_state is not None:
                return reject(ReleaseReasonCode.STALE_EXPECTED_STATE, event)
            if event.to_state is ReleaseState.DRAFT:
                if event.environment is not Environment.STAGING or event.source_record_id is not None or event.promotion_intent:
                    return reject(ReleaseReasonCode.ENVIRONMENT_MISMATCH, event)
            elif event.to_state is ReleaseState.PROMOTION_PENDING:
                source = records.get(event.source_record_id or "")
                if (
                    event.environment is not Environment.PRODUCTION
                    or not event.promotion_intent
                    or source is None
                    or source.state is not ReleaseState.STAGED
                    or source.environment is not Environment.STAGING
                    or source.record_id == event.record_id
                    or source.content_id != event.content_id
                    or source.content_digest != event.content_digest
                ):
                    return reject(ReleaseReasonCode.INVALID_PROMOTION_SOURCE, event)
            else:
                return reject(ReleaseReasonCode.ILLEGAL_TRANSITION, event)
        else:
            if event.expected_state is not existing.state:
                return reject(ReleaseReasonCode.STALE_EXPECTED_STATE, event)
            if event.from_state is not existing.state:
                return reject(ReleaseReasonCode.STALE_EXPECTED_STATE, event)
            if event.content_id != existing.content_id or event.content_digest != existing.content_digest:
                return reject(ReleaseReasonCode.INVALID_EVENT, event)
            if event.to_state is ReleaseState.VALIDATED:
                allowed = existing.state is ReleaseState.DRAFT and event.environment is existing.environment is Environment.STAGING
            elif event.to_state is ReleaseState.STAGED:
                allowed = existing.state is ReleaseState.VALIDATED and event.environment is existing.environment is Environment.STAGING
            elif event.to_state is ReleaseState.PRODUCTION_PROMOTED:
                allowed = existing.state is ReleaseState.PROMOTION_PENDING and event.environment is existing.environment is Environment.PRODUCTION and event.promotion_intent
            elif event.to_state is ReleaseState.FAILED:
                allowed = existing.state in {ReleaseState.DRAFT, ReleaseState.VALIDATED, ReleaseState.STAGED, ReleaseState.PROMOTION_PENDING} and event.environment is existing.environment
            elif event.to_state is ReleaseState.ABORTED:
                allowed = existing.state in {ReleaseState.DRAFT, ReleaseState.VALIDATED, ReleaseState.STAGED, ReleaseState.PROMOTION_PENDING} and event.environment is existing.environment
            elif event.to_state is ReleaseState.SUPERSEDED:
                allowed = existing.state is ReleaseState.PRODUCTION_PROMOTED and event.environment is existing.environment is Environment.PRODUCTION
            elif event.to_state is ReleaseState.ROLLED_BACK:
                target = records.get(event.rollback_to_record_id or "")
                allowed = (
                    existing.state is ReleaseState.PRODUCTION_PROMOTED
                    and event.environment is existing.environment is Environment.PRODUCTION
                    and target is not None
                    and target.state is ReleaseState.PRODUCTION_PROMOTED
                    and target.environment is Environment.PRODUCTION
                    and target.record_id != existing.record_id
                    and target.content_id == event.rollback_to_content_id
                    and target.content_digest == event.rollback_to_digest
                    and target.last_sequence < event.sequence
                )
                if not allowed:
                    return reject(ReleaseReasonCode.UNKNOWN_ROLLBACK_TARGET, event)
            else:
                allowed = False
            if not allowed:
                if event.to_state is ReleaseState.PRODUCTION_PROMOTED:
                    return reject(ReleaseReasonCode.PROMOTION_REQUIRED, event)
                return reject(ReleaseReasonCode.ILLEGAL_TRANSITION, event)

        snapshot = ReleaseStateSnapshot(
            RELEASE_STATE_VERSION, event.record_id,
            event.rollback_to_content_id if event.to_state is ReleaseState.ROLLED_BACK else event.content_id,
            event.rollback_to_digest if event.to_state is ReleaseState.ROLLED_BACK else event.content_digest,
            event.environment, event.to_state, event.sequence,
        )
        records[event.record_id] = snapshot
        if event.to_state is ReleaseState.PRODUCTION_PROMOTED:
            current_production = event.record_id
        elif event.to_state is ReleaseState.ROLLED_BACK:
            current_production = event.rollback_to_record_id
        elif event.to_state is ReleaseState.SUPERSEDED and current_production == event.record_id:
            current_production = None
        seen_events.add(event.event_id)
        seen_transitions.add(event.transition_id)
        previous_digest = event.event_digest

    final_event = events[-1] if events else None
    success = _result(True, ReleaseReasonCode.VALID_TRANSITION, final_event, current_production)
    return ReleaseReplayResult(True, ReleaseReasonCode.VALID_TRANSITION, tuple(records[key] for key in sorted(records)), current_production, success)


__all__ = [
    "RELEASE_STATE_VERSION", "ReleaseEvent", "ReleaseReasonCode", "ReleaseReplayResult",
    "ReleaseState", "ReleaseStateSnapshot", "ReleaseTransitionResult", "make_release_event",
    "replay_release_events", "serialize_release_event", "serialize_release_snapshot",
    "serialize_transition_result",
]
