from __future__ import annotations

import ast
import sys
from dataclasses import replace
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
PIPELINE = ROOT / "content_pipeline"
PACKAGE = PIPELINE / "src" / "scrubbots_content_pipeline"
sys.path.insert(0, str(PIPELINE / "src"))

from scrubbots_content_pipeline import (  # noqa: E402
    Environment,
    ReleaseReasonCode,
    ReleaseState,
    make_release_event,
    replay_release_events,
    serialize_release_event,
    serialize_release_snapshot,
    serialize_transition_result,
)


def _append(
    events: list[object], *, event_id: str, transition_id: str, record_id: str,
    content_id: str, digest: str, environment: Environment,
    from_state: ReleaseState | None, to_state: ReleaseState,
    expected_state: ReleaseState | None, promotion_intent: bool = False,
    source_record_id: str | None = None, rollback_to_record_id: str | None = None,
    rollback_to_content_id: str | None = None, rollback_to_digest: str | None = None,
) -> None:
    prior = events[-1].event_digest if events else "0" * 64  # type: ignore[attr-defined]
    events.append(make_release_event(
        sequence=len(events) + 1, event_id=event_id, transition_id=transition_id,
        record_id=record_id, content_id=content_id, content_digest=digest,
        environment=environment, from_state=from_state, to_state=to_state,
        expected_state=expected_state, previous_event_digest=prior,
        promotion_intent=promotion_intent, source_record_id=source_record_id,
        rollback_to_record_id=rollback_to_record_id,
        rollback_to_content_id=rollback_to_content_id, rollback_to_digest=rollback_to_digest,
    ))


def _history() -> list[object]:
    events: list[object] = []
    for suffix, content, digest in (("a", "content-a", "a" * 64), ("b", "content-b", "b" * 64)):
        staging_record, production_record = f"staging-{suffix}", f"production-{suffix}"
        _append(events, event_id=f"e{len(events)+1}", transition_id=f"t{len(events)+1}", record_id=staging_record,
                content_id=content, digest=digest, environment=Environment.STAGING, from_state=None,
                to_state=ReleaseState.DRAFT, expected_state=None)
        _append(events, event_id=f"e{len(events)+1}", transition_id=f"t{len(events)+1}", record_id=staging_record,
                content_id=content, digest=digest, environment=Environment.STAGING, from_state=ReleaseState.DRAFT,
                to_state=ReleaseState.VALIDATED, expected_state=ReleaseState.DRAFT)
        _append(events, event_id=f"e{len(events)+1}", transition_id=f"t{len(events)+1}", record_id=staging_record,
                content_id=content, digest=digest, environment=Environment.STAGING, from_state=ReleaseState.VALIDATED,
                to_state=ReleaseState.STAGED, expected_state=ReleaseState.VALIDATED)
        _append(events, event_id=f"e{len(events)+1}", transition_id=f"t{len(events)+1}", record_id=production_record,
                content_id=content, digest=digest, environment=Environment.PRODUCTION, from_state=None,
                to_state=ReleaseState.PROMOTION_PENDING, expected_state=None, promotion_intent=True,
                source_record_id=staging_record)
        _append(events, event_id=f"e{len(events)+1}", transition_id=f"t{len(events)+1}", record_id=production_record,
                content_id=content, digest=digest, environment=Environment.PRODUCTION, from_state=ReleaseState.PROMOTION_PENDING,
                to_state=ReleaseState.PRODUCTION_PROMOTED, expected_state=ReleaseState.PROMOTION_PENDING,
                promotion_intent=True)
    _append(events, event_id="e11", transition_id="t11", record_id="production-b",
            content_id="content-b", digest="b" * 64, environment=Environment.PRODUCTION,
            from_state=ReleaseState.PRODUCTION_PROMOTED, to_state=ReleaseState.ROLLED_BACK,
            expected_state=ReleaseState.PRODUCTION_PROMOTED, rollback_to_record_id="production-a",
            rollback_to_content_id="content-a", rollback_to_digest="a" * 64)
    return events


def test_legal_draft_validation_staging_promotion_and_rollback_replay() -> None:
    events = _history()
    result = replay_release_events(events)  # type: ignore[arg-type]
    assert result.accepted
    assert result.reason_code is ReleaseReasonCode.VALID_TRANSITION
    assert result.current_production_record_id == "production-a"
    snapshots = {item.record_id: item for item in result.snapshots}
    assert snapshots["staging-a"].state is ReleaseState.STAGED
    assert snapshots["production-a"].state is ReleaseState.PRODUCTION_PROMOTED
    assert snapshots["production-b"].state is ReleaseState.ROLLED_BACK
    assert snapshots["production-b"].content_id == "content-a"
    assert snapshots["production-b"].last_sequence == 11


def test_direct_draft_to_production_and_illegal_transition_reject() -> None:
    events = _history()[:1]
    _append(events, event_id="illegal", transition_id="illegal-transition", record_id="staging-a",
            content_id="content-a", digest="a" * 64, environment=Environment.PRODUCTION,
            from_state=ReleaseState.DRAFT, to_state=ReleaseState.PRODUCTION_PROMOTED,
            expected_state=ReleaseState.DRAFT)
    result = replay_release_events(events)  # type: ignore[arg-type]
    assert not result.accepted
    assert result.reason_code is ReleaseReasonCode.PROMOTION_REQUIRED


def test_environment_consistency_and_explicit_promotion_source_are_required() -> None:
    events = _history()[:3]
    _append(events, event_id="bad-promotion", transition_id="bad-transition", record_id="production-a",
            content_id="content-a", digest="a" * 64, environment=Environment.PRODUCTION,
            from_state=None, to_state=ReleaseState.PROMOTION_PENDING, expected_state=None,
            source_record_id="staging-a", promotion_intent=False)
    result = replay_release_events(events)  # type: ignore[arg-type]
    assert not result.accepted
    assert result.reason_code is ReleaseReasonCode.INVALID_PROMOTION_SOURCE


@pytest.mark.parametrize("reason", (ReleaseReasonCode.DUPLICATE_EVENT_ID, ReleaseReasonCode.DUPLICATE_TRANSITION_ID))
def test_duplicate_event_or_transition_ids_reject_deterministically(reason: ReleaseReasonCode) -> None:
    events = _history()
    last = events[-1]
    if reason is ReleaseReasonCode.DUPLICATE_EVENT_ID:
        duplicate = replace(last, sequence=12, previous_event_digest=last.event_digest)
    else:
        duplicate = make_release_event(
            sequence=12, event_id="unique-event", transition_id=last.transition_id,
            record_id="staging-c", content_id="content-c", content_digest="c" * 64,
            environment=Environment.STAGING, from_state=None, to_state=ReleaseState.DRAFT,
            expected_state=None, previous_event_digest=last.event_digest,
        )
    result = replay_release_events([*events, duplicate])  # type: ignore[list-item]
    assert not result.accepted
    assert result.reason_code is reason


def test_stale_expected_state_and_unknown_rollback_target_reject() -> None:
    events = _history()[:2]
    _append(events, event_id="stale", transition_id="stale-t", record_id="staging-a",
            content_id="content-a", digest="a" * 64, environment=Environment.STAGING,
            from_state=ReleaseState.DRAFT, to_state=ReleaseState.STAGED,
            expected_state=ReleaseState.DRAFT)
    assert replay_release_events(events).reason_code is ReleaseReasonCode.STALE_EXPECTED_STATE  # type: ignore[arg-type]

    events = _history()[:10]
    _append(events, event_id="bad-rollback", transition_id="bad-rollback-t", record_id="production-b",
            content_id="content-b", digest="b" * 64, environment=Environment.PRODUCTION,
            from_state=ReleaseState.PRODUCTION_PROMOTED, to_state=ReleaseState.ROLLED_BACK,
            expected_state=ReleaseState.PRODUCTION_PROMOTED, rollback_to_record_id="missing",
            rollback_to_content_id="absent", rollback_to_digest="d" * 64)
    assert replay_release_events(events).reason_code is ReleaseReasonCode.UNKNOWN_ROLLBACK_TARGET  # type: ignore[arg-type]


def test_duplicate_replay_tampered_digest_and_reordered_history_are_detected() -> None:
    events = _history()
    duplicate_replay = replay_release_events([*events, events[0]])  # type: ignore[list-item]
    assert duplicate_replay.reason_code is ReleaseReasonCode.DUPLICATE_EVENT_ID
    tampered = [*events]
    tampered[1] = replace(tampered[1], content_id="changed")  # type: ignore[arg-type]
    assert replay_release_events(tampered).reason_code is ReleaseReasonCode.EVENT_DIGEST_MISMATCH  # type: ignore[arg-type]
    reordered = [events[1], events[0], *events[2:]]
    assert replay_release_events(reordered).reason_code is ReleaseReasonCode.INVALID_SEQUENCE  # type: ignore[arg-type]


def test_serialization_is_deterministic_and_history_is_append_only() -> None:
    events = _history()
    result = replay_release_events(events)  # type: ignore[arg-type]
    assert result.accepted
    assert serialize_release_event(events[0]) == serialize_release_event(events[0])  # type: ignore[arg-type]
    assert serialize_release_snapshot(result.snapshots[0]) == serialize_release_snapshot(result.snapshots[0])
    assert serialize_transition_result(result.transition_result) == serialize_transition_result(result.transition_result)
    assert len(events) == 11
    assert len(result.snapshots) == 4
    assert next(item for item in result.snapshots if item.record_id == "staging-a").last_sequence == 3


def test_core_release_state_has_no_wall_clock_random_or_external_side_effects() -> None:
    tree = ast.parse((PACKAGE / "release_state.py").read_text(encoding="utf-8"))
    forbidden_modules = {"datetime", "time", "random", "uuid", "httpx", "requests", "socket", "urllib", "boto3", "godot", "gameplay"}
    forbidden_calls = {"now", "utcnow", "uuid4", "random", "open", "eval", "exec", "__import__"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not {alias.name.split(".", 1)[0] for alias in node.names} & forbidden_modules
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert node.module.split(".", 1)[0] not in forbidden_modules
        elif isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else None
            assert name not in forbidden_calls
