from __future__ import annotations

from datetime import datetime, timezone

from scrubbots_content_pipeline.m17_release_controls import (
    ControlAction,
    DueRevalidationResult,
    ScheduleInstant,
    ScheduleRevision,
    ScheduleState,
    make_schedule_revision,
    normalize_schedule_instant,
    run_due,
)


def _successor(previous: ScheduleRevision, state: ScheduleState) -> ScheduleRevision:
    return make_schedule_revision(
        schedule_id=previous.schedule_id,
        revision=previous.revision + 1,
        state=state,
        candidate_object_key=previous.candidate_object_key,
        candidate_manifest_sha256=previous.candidate_manifest_sha256,
        content_version=previous.content_version,
        expected_current_sha256=previous.expected_current_sha256,
        expected_current_version=previous.expected_current_version,
        target_id=previous.target_id,
        action=previous.action,
        approval_id=previous.approval_id,
        scheduled_at=previous.scheduled_at,
        actor_ref="memory-journal",
        previous_revision_sha256=previous.revision_sha256,
    )


class _MemoryJournal:
    def __init__(self, revision: ScheduleRevision) -> None:
        self.heads = {revision.schedule_id: revision}
        self.claims: dict[str, str] = {}

    def schedule_heads(self) -> dict[str, ScheduleRevision]:
        return dict(self.heads)

    def append_revision(self, revision: ScheduleRevision, *, expected_revision_sha256: str | None) -> bool:
        return False

    def claim_due(self, schedule_id: str, *, expected_revision_sha256: str, claim_key: str) -> bool:
        current = self.heads.get(schedule_id)
        if current is None or current.revision_sha256 != expected_revision_sha256:
            return False
        if current.state is ScheduleState.SCHEDULED:
            self.heads[schedule_id] = _successor(current, ScheduleState.FIRING)
            self.claims[schedule_id] = claim_key
            return True
        return current.state is ScheduleState.FIRING and self.claims.get(schedule_id) == claim_key

    def finish_due(
        self,
        schedule_id: str,
        *,
        expected_revision_sha256: str,
        state: ScheduleState,
        claim_key: str,
    ) -> bool:
        current = self.heads.get(schedule_id)
        if (current is None or current.state is not ScheduleState.FIRING
                or current.revision_sha256 != expected_revision_sha256
                or self.claims.get(schedule_id) != claim_key):
            return False
        self.heads[schedule_id] = _successor(current, state)
        return True


class _FixedClock:
    authority_id = "memory-clock"

    def now_utc(self) -> datetime:
        return datetime(2026, 10, 15, 8, 0, tzinfo=timezone.utc)


def _due_revision() -> ScheduleRevision:
    when = normalize_schedule_instant("2026-10-15T07:00:00Z", "UTC")
    return make_schedule_revision(
        schedule_id="memory-schedule-1",
        revision=1,
        state=ScheduleState.SCHEDULED,
        candidate_object_key="control-candidates/memory-candidate.json",
        candidate_manifest_sha256="a" * 64,
        content_version=2,
        expected_current_sha256="b" * 64,
        expected_current_version=1,
        target_id="staging:default",
        action=ControlAction.DISABLE,
        approval_id="memory-approval-1",
        scheduled_at=ScheduleInstant(
            source_iso8601=when.source_iso8601,
            zone_id=when.zone_id,
            fold=when.fold,
            utc_iso8601=when.utc_iso8601,
        ),
        actor_ref="memory-owner",
        previous_revision_sha256=None,
    )


def test_run_due_memory_revalidates_and_uses_one_stable_activation_key() -> None:
    schedule = _due_revision()
    journal = _MemoryJournal(schedule)
    activation_keys: list[str] = []

    result = run_due(
        journal,
        _FixedClock(),
        lambda _revision: DueRevalidationResult(True, True, True, True),
        lambda _revision, *, idempotency_key: activation_keys.append(idempotency_key) or True,
    )

    assert result.considered == 1
    assert result.claimed == (schedule.schedule_id,)
    assert result.activated == (schedule.schedule_id,)
    assert result.rejected == ()
    assert activation_keys == [f"{schedule.schedule_id}:1:{schedule.candidate_manifest_sha256}"]
    assert journal.schedule_heads()[schedule.schedule_id].state is ScheduleState.FIRED

    blocked_journal = _MemoryJournal(schedule)
    blocked_activation_calls: list[str] = []
    blocked = run_due(
        blocked_journal,
        _FixedClock(),
        lambda _revision: DueRevalidationResult(True, True, False, True),
        lambda _revision, *, idempotency_key: blocked_activation_calls.append(idempotency_key) or True,
    )

    assert blocked.activated == ()
    assert blocked.rejected == ((schedule.schedule_id, "DUE_REVALIDATION_REJECTED"),)
    assert blocked_activation_calls == []
    assert blocked_journal.schedule_heads()[schedule.schedule_id].state is ScheduleState.BLOCKED
