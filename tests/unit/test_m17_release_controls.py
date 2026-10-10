from __future__ import annotations

import hashlib
import sqlite3
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))

from scrubbots_content_pipeline.config import Environment
from scrubbots_content_pipeline.current_main_replay import CurrentMainReplayReceipt, REPOSITORY
from scrubbots_content_pipeline.manifest_history import ManifestHistoryV1, append_manifest_history
from scrubbots_content_pipeline.manifest_v1 import ContentManifestV1, ManifestLevelV1, ManifestPackV1
from scrubbots_content_pipeline.m17_release_controls import (
    BoundOwnerApproval,
    ControlAction,
    DueRevalidationResult,
    ReleaseControlError,
    ReceiptOperation,
    ScheduleInstant,
    ScheduleState,
    ScheduleVerification,
    cancel_schedule,
    create_schedule_revision,
    edit_schedule,
    make_control_receipt,
    make_weekly_accepted_batch,
    normalize_schedule_instant,
    parse_schedule_revision,
    prepare_disable_candidate,
    prepare_rollback_candidate,
    render_control_receipt,
    run_due,
    select_known_good,
    serialize_control_receipt,
    serialize_schedule_revision,
    supersede_schedule,
    validate_schedule_transition,
)
from scrubbots_content_pipeline.provider import ProviderIdentity, ProviderObjectBytesResult, ProviderResultCategory


PACK = b"fixture scrubpack v1"
PACK_SHA = hashlib.sha256(PACK).hexdigest()
TARGET = "production:default"
NOW = datetime(2026, 10, 10, 14, 0, tzinfo=timezone.utc)


def _manifest(version: int, *, disabled: tuple[str, ...] = (), minimum_game_version: str = "0.0.0") -> bytes:
    return ContentManifestV1(
        packs=(ManifestPackV1("campaign", 1, "packs/campaign/v1.scrubpack", PACK_SHA, len(PACK)),),
        levels=(ManifestLevelV1("Level-01", "campaign"), ManifestLevelV1("Level-02", "campaign")),
        content_version=version,
        minimum_game_version=minimum_game_version,
        disabled_levels=disabled,
    ).to_json_bytes()


class SQLiteLocalProvider:
    """Small local SQLite object/history provider; never connects to a remote service."""

    identity = ProviderIdentity("m17-local-stateful", "1.0")

    def __init__(self, path: Path | sqlite3.Connection):
        self._connection = path if isinstance(path, sqlite3.Connection) else None
        self.path = None if self._connection is not None else path
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS objects (environment TEXT, object_key TEXT, raw BLOB, PRIMARY KEY(environment, object_key))")
            db.execute("CREATE TABLE IF NOT EXISTS schedule_revisions (schedule_id TEXT, revision INTEGER, digest TEXT UNIQUE, raw BLOB, PRIMARY KEY(schedule_id, revision))")
            db.execute("CREATE TABLE IF NOT EXISTS schedule_claims (schedule_id TEXT PRIMARY KEY, claim_key TEXT UNIQUE)")
            db.execute("CREATE TABLE IF NOT EXISTS active_state (slot INTEGER PRIMARY KEY CHECK(slot=1), manifest BLOB, history BLOB)")

    def _connect(self, *, timeout: float = 5.0) -> sqlite3.Connection:
        if self._connection is not None:
            return self._connection
        assert self.path is not None
        return sqlite3.connect(self.path, timeout=timeout)

    def put_object(self, environment: Environment, key: str, raw: bytes) -> None:
        with self._connect() as db:
            db.execute("INSERT OR REPLACE INTO objects VALUES (?, ?, ?)", (environment.value, key, raw))

    def read_object_bytes(self, environment: Environment, object_key: str) -> ProviderObjectBytesResult:
        with self._connect() as db:
            row = db.execute("SELECT raw FROM objects WHERE environment=? AND object_key=?", (environment.value, object_key)).fetchone()
        return ProviderObjectBytesResult(
            "1.0", ProviderResultCategory.SUCCESS, self.identity.provider_id, environment,
            object_key, None if row is None else bytes(row[0]),
        )

    def initialize_active(self, manifest: bytes, history: bytes) -> None:
        with self._connect() as db:
            db.execute("INSERT OR REPLACE INTO active_state VALUES (1, ?, ?)", (manifest, history))

    def read_active(self) -> tuple[bytes, bytes]:
        with self._connect() as db:
            row = db.execute("SELECT manifest, history FROM active_state WHERE slot=1").fetchone()
        assert row is not None
        return bytes(row[0]), bytes(row[1])

    def compare_and_swap_active(self, expected_sha: str, expected_version: int, manifest: bytes, history: bytes) -> bool:
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT manifest FROM active_state WHERE slot=1").fetchone()
            if row is None or hashlib.sha256(bytes(row[0])).hexdigest() != expected_sha:
                db.rollback()
                return False
            if int(__import__("json").loads(bytes(row[0]).decode())["content_version"]) != expected_version:
                db.rollback()
                return False
            db.execute("UPDATE active_state SET manifest=?, history=? WHERE slot=1", (manifest, history))
            db.commit()
            return True

    def schedule_heads(self):
        from scrubbots_content_pipeline.m17_release_controls import parse_schedule_revision
        with self._connect() as db:
            rows = db.execute("SELECT raw FROM schedule_revisions r WHERE revision=(SELECT MAX(revision) FROM schedule_revisions WHERE schedule_id=r.schedule_id)").fetchall()
        items = [parse_schedule_revision(bytes(row[0])) for row in rows]
        return {item.schedule_id: item for item in items}

    def append_revision(self, revision, *, expected_revision_sha256):
        from scrubbots_content_pipeline.m17_release_controls import parse_schedule_revision, serialize_schedule_revision
        with self._connect(timeout=5) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT raw FROM schedule_revisions WHERE schedule_id=? ORDER BY revision DESC LIMIT 1", (revision.schedule_id,)).fetchone()
            previous = parse_schedule_revision(bytes(row[0])) if row else None
            actual = previous.revision_sha256 if previous else None
            if actual != expected_revision_sha256:
                db.rollback()
                return False
            valid = validate_schedule_transition(previous, revision)
            if not valid:
                db.rollback()
                return False
            db.execute("INSERT INTO schedule_revisions VALUES (?, ?, ?, ?)",
                       (revision.schedule_id, revision.revision, revision.revision_sha256,
                        serialize_schedule_revision(revision)))
            db.commit()
            return True

    def claim_due(self, schedule_id: str, *, expected_revision_sha256: str, claim_key: str) -> bool:
        from scrubbots_content_pipeline.m17_release_controls import make_schedule_revision, serialize_schedule_revision
        with self._connect(timeout=5) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT raw FROM schedule_revisions WHERE schedule_id=? ORDER BY revision DESC LIMIT 1", (schedule_id,)).fetchone()
            if row is None:
                db.rollback()
                return False
            previous = parse_schedule_revision(bytes(row[0]))
            if previous.revision_sha256 != expected_revision_sha256:
                db.rollback()
                return False
            if previous.state is ScheduleState.FIRING:
                claim = db.execute("SELECT claim_key FROM schedule_claims WHERE schedule_id=?", (schedule_id,)).fetchone()
                db.rollback()
                return claim is not None and claim[0] == claim_key
            if previous.state is not ScheduleState.SCHEDULED:
                db.rollback()
                return False
            try:
                db.execute("INSERT INTO schedule_claims VALUES (?, ?)", (schedule_id, claim_key))
            except sqlite3.IntegrityError:
                db.rollback()
                return False
            firing = make_schedule_revision(
                schedule_id=schedule_id, revision=previous.revision + 1, state=ScheduleState.FIRING,
                candidate_object_key=previous.candidate_object_key,
                candidate_manifest_sha256=previous.candidate_manifest_sha256,
                content_version=previous.content_version,
                expected_current_sha256=previous.expected_current_sha256,
                expected_current_version=previous.expected_current_version,
                target_id=previous.target_id, action=previous.action, approval_id=previous.approval_id,
                scheduled_at=previous.scheduled_at, actor_ref="run-due",
                previous_revision_sha256=previous.revision_sha256,
            )
            if not validate_schedule_transition(previous, firing):
                db.rollback()
                return False
            db.execute("INSERT INTO schedule_revisions VALUES (?, ?, ?, ?)",
                       (schedule_id, firing.revision, firing.revision_sha256, serialize_schedule_revision(firing)))
            db.commit()
            return True

    def finish_due(self, schedule_id: str, *, expected_revision_sha256: str,
                   state: ScheduleState, claim_key: str) -> bool:
        from scrubbots_content_pipeline.m17_release_controls import make_schedule_revision, serialize_schedule_revision
        if state not in {ScheduleState.FIRED, ScheduleState.BLOCKED}:
            return False
        with self._connect(timeout=5) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT raw FROM schedule_revisions WHERE schedule_id=? ORDER BY revision DESC LIMIT 1", (schedule_id,)).fetchone()
            claim = db.execute("SELECT claim_key FROM schedule_claims WHERE schedule_id=?", (schedule_id,)).fetchone()
            if row is None or claim is None or claim[0] != claim_key:
                db.rollback()
                return False
            previous = parse_schedule_revision(bytes(row[0]))
            if previous.revision_sha256 != expected_revision_sha256 or previous.state is not ScheduleState.FIRING:
                db.rollback()
                return False
            finished = make_schedule_revision(
                schedule_id=schedule_id, revision=previous.revision + 1, state=state,
                candidate_object_key=previous.candidate_object_key,
                candidate_manifest_sha256=previous.candidate_manifest_sha256,
                content_version=previous.content_version,
                expected_current_sha256=previous.expected_current_sha256,
                expected_current_version=previous.expected_current_version,
                target_id=previous.target_id, action=previous.action, approval_id=previous.approval_id,
                scheduled_at=previous.scheduled_at, actor_ref="run-due",
                previous_revision_sha256=previous.revision_sha256,
            )
            if not validate_schedule_transition(previous, finished):
                db.rollback()
                return False
            db.execute("INSERT INTO schedule_revisions VALUES (?, ?, ?, ?)",
                       (schedule_id, finished.revision, finished.revision_sha256, serialize_schedule_revision(finished)))
            db.commit()
            return True


class FixedClock:
    authority_id = "fixture-clock"

    def __init__(self, now: datetime):
        self.value = now

    def now_utc(self) -> datetime:
        return self.value


def _history(*manifests: bytes) -> ManifestHistoryV1:
    result = ManifestHistoryV1()
    for index, raw in enumerate(manifests, 1):
        result = append_manifest_history(result, raw, recorded_at_utc=f"2026-10-10T13:00:{index:02d}Z")
    return result


def _approval_for(action: ControlAction, current: bytes, candidate: bytes) -> BoundOwnerApproval:
    return BoundOwnerApproval(
        "approval-1", "owner-1", action, TARGET,
        __import__("json").loads(current)["content_version"], hashlib.sha256(current).hexdigest(),
        __import__("json").loads(candidate)["content_version"], hashlib.sha256(candidate).hexdigest(),
    )


def _schedule_verification(candidate) -> ScheduleVerification:
    manifest = ContentManifestV1.from_dict(__import__("json").loads(candidate.manifest_bytes))
    receipt = _replay_receipt(candidate.manifest_bytes, "c")
    return ScheduleVerification(
        candidate.manifest_sha256, candidate.approval.approval_id, True, True,
        tuple((item.pack_id, item.sha256, item.byte_length) for item in manifest.packs), receipt,
    )


def _replay_receipt(raw: bytes, commit_letter: str, target: str = "STAGING") -> CurrentMainReplayReceipt:
    manifest = ContentManifestV1.from_dict(__import__("json").loads(raw))
    rows = []
    for pack in manifest.packs:
        rows.append({
            "pack_id": pack.pack_id,
            "pack_sha256": pack.sha256,
            "levels": [{
                "level_id": level.level_id, "accepted": True, "solver_status": "SOLVED",
                "replay_solved": True, "unresolved": 0,
            } for level in manifest.levels if level.pack_id == pack.pack_id],
        })
    return CurrentMainReplayReceipt(True, "VERIFIED", REPOSITORY, "main", commit_letter * 40, {},
                                    hashlib.sha256(raw).hexdigest(), tuple(rows), target)


def test_known_good_selection_verifies_history_pack_bytes_and_current_main_receipt(tmp_path: Path) -> None:
    good = _manifest(1, minimum_game_version="1.0.0")
    newer = _manifest(2, disabled=("Level-01",))
    history = _history(good, newer)
    provider = SQLiteLocalProvider(tmp_path / "state.db")
    provider.put_object(Environment.PRODUCTION, "packs/campaign/v1.scrubpack", PACK)
    target_sha = history.records[0].manifest_sha256

    def replay(raw, packs):
        assert packs == {"campaign": PACK}
        return _replay_receipt(raw, "a", "PRODUCTION")

    found = select_known_good(history, target_sha, provider, Environment.PRODUCTION, replay,
                              current_game_version="1.0.0",
                              supported_manifest_schema_versions={"scrubbots.content.manifest.v1": (1,)})
    assert found.record.manifest_bytes == good
    assert found.pack_bytes == (("campaign", PACK),)

    with pytest.raises(ReleaseControlError, match="KNOWN_GOOD_COMPATIBILITY_FAILED"):
        select_known_good(history, target_sha, provider, Environment.PRODUCTION, replay,
                          current_game_version="0.9.0",
                          supported_manifest_schema_versions={"scrubbots.content.manifest.v1": (1,)})

    provider.put_object(Environment.PRODUCTION, "packs/campaign/v1.scrubpack", b"corrupt")
    with pytest.raises(ReleaseControlError, match="KNOWN_GOOD_PACK_INTEGRITY_FAILED"):
        select_known_good(history, target_sha, provider, Environment.PRODUCTION, replay,
                          current_game_version="1.0.0",
                          supported_manifest_schema_versions={"scrubbots.content.manifest.v1": (1,)})


def test_rollback_is_monotonic_owner_bound_and_statefully_read_back(tmp_path: Path) -> None:
    good = _manifest(1)
    bad = _manifest(2, disabled=("Level-01",))
    current_history = _history(good, bad)
    provider = SQLiteLocalProvider(tmp_path / "state.db")
    provider.put_object(Environment.PRODUCTION, "packs/campaign/v1.scrubpack", PACK)
    provider.initialize_active(bad, __import__("scrubbots_content_pipeline.manifest_history", fromlist=["serialize_manifest_history"]).serialize_manifest_history(current_history))
    record = current_history.records[0]
    receipt = _replay_receipt(record.manifest_bytes, "b", "PRODUCTION")
    known = select_known_good(current_history, record.manifest_sha256, provider, Environment.PRODUCTION,
                              lambda _raw, _packs: receipt, current_game_version="1.0.0",
                              supported_manifest_schema_versions={"scrubbots.content.manifest.v1": (1,)})
    intended = ContentManifestV1(
        packs=known.manifest.packs, levels=known.manifest.levels,
        content_version=3, minimum_game_version=known.manifest.minimum_game_version,
        disabled_levels=known.manifest.disabled_levels, schedules=known.manifest.schedules,
    ).to_json_bytes()
    approval = _approval_for(ControlAction.ROLLBACK, bad, intended)
    candidate = prepare_rollback_candidate(
        bad, current_history, known, target_id=TARGET, reason="restore last known good",
        approval=approval, approval_check=lambda: approval, recorded_at_utc="2026-10-10T14:00:00Z",
    )
    assert __import__("json").loads(candidate.manifest_bytes)["content_version"] == 3
    assert candidate.manifest_sha256 == hashlib.sha256(candidate.manifest_bytes).hexdigest()
    assert candidate.history.records[-1].manifest_bytes == candidate.manifest_bytes
    serialized_history = __import__("scrubbots_content_pipeline.manifest_history", fromlist=["serialize_manifest_history"]).serialize_manifest_history(candidate.history)
    assert provider.compare_and_swap_active(candidate.expected_current_sha256, 2, candidate.manifest_bytes, serialized_history)
    readback, readback_history = provider.read_active()
    assert readback == candidate.manifest_bytes
    assert __import__("scrubbots_content_pipeline.manifest_history", fromlist=["parse_manifest_history"]).parse_manifest_history(readback_history) == candidate.history
    assert not provider.compare_and_swap_active(candidate.expected_current_sha256, 2, candidate.manifest_bytes, serialized_history)

    stale = BoundOwnerApproval("approval-1", "owner-1", ControlAction.ROLLBACK, TARGET, 1,
                               hashlib.sha256(good).hexdigest(), 3, candidate.manifest_sha256)
    with pytest.raises(ReleaseControlError, match="OWNER_APPROVAL_SCOPE_MISMATCH"):
        prepare_rollback_candidate(bad, current_history, known, target_id=TARGET, reason="stale",
                                   approval=stale, approval_check=lambda: stale,
                                   recorded_at_utc="2026-10-10T14:00:00Z")


def test_disable_reenable_changes_only_selected_declarative_state_and_rejects_invalid_ids() -> None:
    current = _manifest(1)
    history = _history(current)
    changed = ContentManifestV1(
        packs=ContentManifestV1.from_dict(__import__("json").loads(current)).packs,
        levels=ContentManifestV1.from_dict(__import__("json").loads(current)).levels,
        content_version=2, disabled_levels=("Level-02",),
    ).to_json_bytes()
    approval = _approval_for(ControlAction.DISABLE, current, changed)
    candidate = prepare_disable_candidate(
        current, history, ("Level-02",), disabled=True, target_id=TARGET, reason="unsafe level",
        approval=approval, approval_check=lambda: approval, recorded_at_utc="2026-10-10T14:00:00Z",
    )
    before = ContentManifestV1.from_dict(__import__("json").loads(current))
    after = ContentManifestV1.from_dict(__import__("json").loads(candidate.manifest_bytes))
    assert after.content_version == 2
    assert after.disabled_levels == ("Level-02",)
    assert after.levels == before.levels and after.packs == before.packs

    with pytest.raises(ReleaseControlError, match="DUPLICATE_LEVEL_SELECTION"):
        prepare_disable_candidate(current, history, ("Level-02", "level-02"), disabled=True,
                                  target_id=TARGET, reason="duplicate", approval=approval,
                                  approval_check=lambda: approval, recorded_at_utc="2026-10-10T14:00:00Z")
    with pytest.raises(ReleaseControlError, match="UNKNOWN_LEVEL_ID"):
        prepare_disable_candidate(current, history, ("Level-03",), disabled=True,
                                  target_id=TARGET, reason="unknown", approval=approval,
                                  approval_check=lambda: approval, recorded_at_utc="2026-10-10T14:00:00Z")

    disabled_history = _history(current, candidate.manifest_bytes)
    desired_reenable = ContentManifestV1(
        packs=before.packs, levels=before.levels, content_version=3,
    ).to_json_bytes()
    reenable_approval = _approval_for(ControlAction.REENABLE, candidate.manifest_bytes, desired_reenable)
    reenabled = prepare_disable_candidate(
        candidate.manifest_bytes, disabled_history, ("Level-02",), disabled=False,
        target_id=TARGET, reason="restore level", approval=reenable_approval,
        approval_check=lambda: reenable_approval, recorded_at_utc="2026-10-10T14:01:00Z",
    )
    reenabled_manifest = ContentManifestV1.from_dict(__import__("json").loads(reenabled.manifest_bytes))
    assert reenabled_manifest.disabled_levels == () and reenabled_manifest.packs == before.packs


def test_timezone_offset_gap_fold_roundtrip_and_schedule_revisions(tmp_path: Path) -> None:
    early = normalize_schedule_instant("2026-11-01T01:30:00-04:00", "America/New_York")
    late = normalize_schedule_instant("2026-11-01T01:30:00-05:00", "America/New_York")
    assert (early.fold, early.utc_iso8601) == (0, "2026-11-01T05:30:00Z")
    assert (late.fold, late.utc_iso8601) == (1, "2026-11-01T06:30:00Z")
    with pytest.raises(ReleaseControlError, match="NONEXISTENT_LOCAL_TIME"):
        normalize_schedule_instant("2026-03-08T02:30:00-05:00", "America/New_York")
    with pytest.raises(ReleaseControlError, match="TIMEZONE_OFFSET_MISMATCH"):
        normalize_schedule_instant("2026-11-01T01:30:00-06:00", "America/New_York")

    current = _manifest(1)
    history = _history(current)
    candidate_bytes = ContentManifestV1(
        packs=ContentManifestV1.from_dict(__import__("json").loads(current)).packs,
        levels=ContentManifestV1.from_dict(__import__("json").loads(current)).levels,
        content_version=2, disabled_levels=("Level-01",),
    ).to_json_bytes()
    approval = _approval_for(ControlAction.DISABLE, current, candidate_bytes)
    candidate = prepare_disable_candidate(
        current, history, ("Level-01",), disabled=True, target_id=TARGET, reason="disable",
        approval=approval, approval_check=lambda: approval,
        recorded_at_utc="2026-10-10T14:00:00Z",
    )
    schedule = create_schedule_revision(
        candidate, schedule_id="sched-1", candidate_object_key="control-candidates/sha256-abc.json",
        scheduled_at=normalize_schedule_instant("2026-10-11T10:00:00+03:00", "Europe/Istanbul"),
        actor_ref="owner-1", clock=FixedClock(NOW), verification=_schedule_verification(candidate),
    )
    assert parse_schedule_revision(serialize_schedule_revision(schedule)) == schedule
    store = SQLiteLocalProvider(tmp_path / "schedule.db")
    assert store.append_revision(schedule, expected_revision_sha256=None)
    persisted = SQLiteLocalProvider(tmp_path / "schedule.db").schedule_heads()["sched-1"]
    scheduled_receipt = make_control_receipt(
        actor_ref="owner-1", operation=ReceiptOperation.SCHEDULE,
        occurred_at_utc="2026-10-10T14:00:00Z", target_id=TARGET,
        current_version=1, next_version=2, prior_manifest_sha256=candidate.expected_current_sha256,
        new_manifest_sha256=candidate.manifest_sha256, pack_hashes=(("campaign", PACK_SHA),),
        approval_id=candidate.approval.approval_id, provider_record_sha256=persisted.revision_sha256,
        outcome="INTENT_PERSISTED",
    )
    assert parse_schedule_revision(serialize_schedule_revision(persisted)) == persisted
    assert serialize_control_receipt(scheduled_receipt)
    scheduled_receipt = make_control_receipt(
        actor_ref="owner-1", operation=ReceiptOperation.SCHEDULE,
        occurred_at_utc="2026-10-10T14:00:00Z", target_id=TARGET,
        current_version=1, next_version=2, prior_manifest_sha256=candidate.expected_current_sha256,
        new_manifest_sha256=candidate.manifest_sha256, pack_hashes=(("campaign", PACK_SHA),),
        approval_id=candidate.approval.approval_id, provider_record_sha256=persisted.revision_sha256,
        outcome="INTENT_PERSISTED",
    )
    assert parse_schedule_revision(serialize_schedule_revision(persisted)) == persisted
    assert serialize_control_receipt(scheduled_receipt)
    edited = edit_schedule(
        persisted, candidate, candidate_object_key="control-candidates/edited.json",
        scheduled_at=normalize_schedule_instant("2026-10-12T10:00:00+03:00", "Europe/Istanbul"),
        actor_ref="owner-1", clock=FixedClock(NOW), verification=_schedule_verification(candidate),
    )
    assert store.append_revision(edited, expected_revision_sha256=persisted.revision_sha256)
    assert store.schedule_heads()["sched-1"].revision == 2
    cancel = cancel_schedule(edited, actor_ref="owner-1")
    assert store.append_revision(cancel, expected_revision_sha256=edited.revision_sha256)
    assert store.schedule_heads()["sched-1"].state is ScheduleState.CANCELLED
    cancelled_receipt = make_control_receipt(
        actor_ref="owner-1", operation=ReceiptOperation.CANCEL_SCHEDULE,
        occurred_at_utc="2026-10-10T14:01:00Z", target_id=TARGET,
        current_version=1, next_version=2, prior_manifest_sha256=candidate.expected_current_sha256,
        new_manifest_sha256=candidate.manifest_sha256, pack_hashes=(("campaign", PACK_SHA),),
        approval_id=candidate.approval.approval_id, provider_record_sha256=cancel.revision_sha256,
        outcome="INTENT_CANCELLED",
    )
    assert serialize_control_receipt(cancelled_receipt)
    cancelled_receipt = make_control_receipt(
        actor_ref="owner-1", operation=ReceiptOperation.CANCEL_SCHEDULE,
        occurred_at_utc="2026-10-10T14:01:00Z", target_id=TARGET,
        current_version=1, next_version=2, prior_manifest_sha256=candidate.expected_current_sha256,
        new_manifest_sha256=candidate.manifest_sha256, pack_hashes=(("campaign", PACK_SHA),),
        approval_id=candidate.approval.approval_id, provider_record_sha256=cancel.revision_sha256,
        outcome="INTENT_CANCELLED",
    )
    assert serialize_control_receipt(cancelled_receipt)
    with pytest.raises(ReleaseControlError, match="SCHEDULE_NOT_EDITABLE"):
        supersede_schedule(cancel, actor_ref="owner-1")


def test_due_run_claim_is_atomic_revalidates_and_only_activates_when_all_checks_pass(tmp_path: Path) -> None:
    current = _manifest(1)
    history = _history(current)
    after = ContentManifestV1(
        packs=ContentManifestV1.from_dict(__import__("json").loads(current)).packs,
        levels=ContentManifestV1.from_dict(__import__("json").loads(current)).levels,
        content_version=2, disabled_levels=("Level-01",),
    ).to_json_bytes()
    approval = _approval_for(ControlAction.DISABLE, current, after)
    candidate = prepare_disable_candidate(
        current, history, ("Level-01",), disabled=True, target_id=TARGET, reason="schedule",
        approval=approval, approval_check=lambda: approval, recorded_at_utc="2026-10-10T14:00:00Z",
    )
    schedule = create_schedule_revision(
        candidate, schedule_id="due-1", candidate_object_key="control-candidates/candidate.json",
        scheduled_at=ScheduleInstant("2026-10-10T15:00:00+00:00", "UTC", 0, "2026-10-10T15:00:00Z"),
        actor_ref="owner-1", clock=FixedClock(NOW), verification=_schedule_verification(candidate),
    )
    store = SQLiteLocalProvider(tmp_path / "due.db")
    assert store.append_revision(schedule, expected_revision_sha256=None)
    calls: list[str] = []
    result = run_due(
        store,
        FixedClock(datetime(2026, 10, 10, 15, 0, tzinfo=timezone.utc)),
        lambda _revision: DueRevalidationResult(True, True, True, True),
        lambda _revision, *, idempotency_key: calls.append(idempotency_key) or True,
    )
    assert result.claimed == ("due-1",) and result.activated == ("due-1",)
    assert calls == ["due-1:1:" + candidate.manifest_sha256]
    assert store.schedule_heads()["due-1"].state is ScheduleState.FIRED

    blocked = SQLiteLocalProvider(tmp_path / "blocked.db")
    assert blocked.append_revision(schedule, expected_revision_sha256=None)
    not_run = run_due(
        blocked, FixedClock(datetime(2026, 10, 10, 15, 0, tzinfo=timezone.utc)),
        lambda _revision: DueRevalidationResult(True, False, True, True),
        lambda _revision, *, idempotency_key: pytest.fail("must not activate stale approval"),
    )
    assert not_run.rejected == (("due-1", "DUE_REVALIDATION_REJECTED"),)
    assert blocked.schedule_heads()["due-1"].state is ScheduleState.BLOCKED


def test_cancel_vs_due_claim_uses_revision_cas_and_cannot_fire_cancelled_intent(tmp_path: Path) -> None:
    current = _manifest(1)
    history = _history(current)
    desired = ContentManifestV1(
        packs=ContentManifestV1.from_dict(__import__("json").loads(current)).packs,
        levels=ContentManifestV1.from_dict(__import__("json").loads(current)).levels,
        content_version=2, disabled_levels=("Level-01",),
    ).to_json_bytes()
    approval = _approval_for(ControlAction.DISABLE, current, desired)
    candidate = prepare_disable_candidate(
        current, history, ("Level-01",), disabled=True, target_id=TARGET, reason="race",
        approval=approval, approval_check=lambda: approval, recorded_at_utc="2026-10-10T14:00:00Z",
    )
    scheduled = create_schedule_revision(
        candidate, schedule_id="race-1", candidate_object_key="control-candidates/race.json",
        scheduled_at=ScheduleInstant("2026-10-10T15:00:00+00:00", "UTC", 0, "2026-10-10T15:00:00Z"),
        actor_ref="owner-1", clock=FixedClock(NOW), verification=_schedule_verification(candidate),
    )
    store = SQLiteLocalProvider(tmp_path / "race.db")
    assert store.append_revision(scheduled, expected_revision_sha256=None)
    barrier = threading.Barrier(3)
    outcomes: dict[str, object] = {}
    activated: list[str] = []

    def cancel_worker() -> None:
        barrier.wait()
        cancellation = cancel_schedule(scheduled, actor_ref="owner-1")
        outcomes["cancel"] = store.append_revision(cancellation,
                                                  expected_revision_sha256=scheduled.revision_sha256)

    def due_worker() -> None:
        barrier.wait()
        outcomes["due"] = run_due(
            store, FixedClock(datetime(2026, 10, 10, 15, 0, tzinfo=timezone.utc)),
            lambda _revision: DueRevalidationResult(True, True, True, True),
            lambda _revision, *, idempotency_key: activated.append(idempotency_key) or True,
        )

    workers = (threading.Thread(target=cancel_worker), threading.Thread(target=due_worker))
    for worker in workers:
        worker.start()
    barrier.wait()
    for worker in workers:
        worker.join(timeout=10)
        assert not worker.is_alive()
    final = store.schedule_heads()["race-1"]
    assert final.state in {ScheduleState.CANCELLED, ScheduleState.FIRED}
    if final.state is ScheduleState.CANCELLED:
        assert outcomes["cancel"] is True and not activated
    else:
        assert outcomes["cancel"] is False and len(activated) == 1


def test_receipts_are_deterministic_and_weekly_batches_keep_distinct_lineage() -> None:
    sha = "a" * 64
    receipt = make_control_receipt(
        actor_ref="owner-1", operation=ControlAction.DISABLE,
        occurred_at_utc="2026-10-10T14:00:00Z", target_id=TARGET,
        current_version=1, next_version=2, prior_manifest_sha256=sha,
        new_manifest_sha256="b" * 64, pack_hashes=(("campaign", PACK_SHA),),
        approval_id="approval-1", provider_record_sha256="c" * 64, outcome="PREPARED",
    )
    assert serialize_control_receipt(receipt) == serialize_control_receipt(receipt)
    assert receipt.report_sha256 in render_control_receipt(receipt)
    batch_a = make_weekly_accepted_batch("batch-a", "2026-W41", ("candidate-a",), sha, "b" * 64, "c" * 64)
    batch_b = make_weekly_accepted_batch("batch-b", "2026-W41", ("candidate-b",), sha, "d" * 64, "e" * 64)
    assert batch_a.immutable_identity_sha256 != batch_b.immutable_identity_sha256
    with pytest.raises(ReleaseControlError, match="INVALID_WEEKLY_BATCH"):
        make_weekly_accepted_batch("batch-a", "2026-W41", ("candidate-a", "candidate-a"), sha, "b" * 64, "c" * 64)


def _f02_scheduled_intent(schedule_id: str):
    current = _manifest(1)
    current_manifest = ContentManifestV1.from_dict(__import__("json").loads(current))
    desired = ContentManifestV1(
        packs=current_manifest.packs, levels=current_manifest.levels,
        content_version=2, disabled_levels=("Level-01",),
    ).to_json_bytes()
    approval = _approval_for(ControlAction.DISABLE, current, desired)
    candidate = prepare_disable_candidate(
        current, _history(current), ("Level-01",), disabled=True,
        target_id=TARGET, reason="F02 interrupted FIRING recovery",
        approval=approval, approval_check=lambda: approval,
        recorded_at_utc="2026-10-10T14:00:00Z",
    )
    scheduled = create_schedule_revision(
        candidate, schedule_id=schedule_id, candidate_object_key=f"control-candidates/{schedule_id}.json",
        scheduled_at=ScheduleInstant(
            "2026-10-10T15:00:00+00:00", "UTC", 0, "2026-10-10T15:00:00Z",
        ),
        actor_ref="owner-1", clock=FixedClock(NOW), verification=_schedule_verification(candidate),
    )
    return candidate, scheduled


class SimulatedProcessInterruption(BaseException):
    """Models abrupt process loss that normal exception handling cannot absorb."""


@pytest.mark.parametrize("crash_point", ("before_activation", "after_activation_before_finalize"))
def test_f02_interrupted_firing_reuses_original_claim_and_activation_key_without_duplicate_effects(
    crash_point: str, monkeypatch: pytest.MonkeyPatch,
) -> None:
    from scrubbots_content_pipeline.m17_release_controls import DueRevalidationResult

    candidate, scheduled = _f02_scheduled_intent(f"f02-{crash_point}")
    store = SQLiteLocalProvider(sqlite3.connect(":memory:"))
    assert store.append_revision(scheduled, expected_revision_sha256=None)
    key = f"{scheduled.schedule_id}:{scheduled.revision}:{candidate.manifest_sha256}"
    revalidated_states: list[ScheduleState] = []
    activation_keys: list[str] = []
    activation_effects: set[str] = set()
    activation_side_effects: list[str] = []

    def revalidate(revision):
        revalidated_states.append(revision.state)
        if crash_point == "before_activation" and len(revalidated_states) == 1:
            raise SimulatedProcessInterruption()
        return DueRevalidationResult(True, True, True, True)

    def activate(_revision, *, idempotency_key: str) -> bool:
        activation_keys.append(idempotency_key)
        if idempotency_key not in activation_effects:
            activation_effects.add(idempotency_key)
            activation_side_effects.append(idempotency_key)
        return True

    original_finish = store.finish_due
    interrupted_finalize = False

    def interrupt_first_finalize(schedule_id, *, expected_revision_sha256, state, claim_key):
        nonlocal interrupted_finalize
        if crash_point == "after_activation_before_finalize" and state is ScheduleState.FIRED and not interrupted_finalize:
            interrupted_finalize = True
            raise SimulatedProcessInterruption()
        return original_finish(
            schedule_id, expected_revision_sha256=expected_revision_sha256,
            state=state, claim_key=claim_key,
        )

    monkeypatch.setattr(store, "finish_due", interrupt_first_finalize)
    with pytest.raises(SimulatedProcessInterruption):
        run_due(
            store, FixedClock(datetime(2026, 10, 10, 15, 0, tzinfo=timezone.utc)),
            revalidate, activate,
        )

    firing = store.schedule_heads()[scheduled.schedule_id]
    assert firing.state is ScheduleState.FIRING
    persisted_claim = store._connect().execute(
        "SELECT claim_key FROM schedule_claims WHERE schedule_id=?", (scheduled.schedule_id,),
    ).fetchone()
    assert persisted_claim == (key,)
    if crash_point == "before_activation":
        assert activation_keys == [] and activation_effects == set() and activation_side_effects == []
    else:
        assert activation_keys == [key] and activation_effects == {key} and activation_side_effects == [key]

    monkeypatch.setattr(store, "finish_due", original_finish)
    recovered = run_due(
        store, FixedClock(datetime(2026, 10, 10, 15, 0, tzinfo=timezone.utc)),
        revalidate, activate,
    )
    assert recovered.activated == (scheduled.schedule_id,)
    assert recovered.rejected == ()
    assert revalidated_states == [ScheduleState.FIRING, ScheduleState.FIRING]
    assert activation_keys == ([key] if crash_point == "before_activation" else [key, key])
    assert activation_effects == {key}
    assert activation_side_effects == [key]
    assert store.schedule_heads()[scheduled.schedule_id].state is ScheduleState.FIRED

    already_finished = run_due(
        store, FixedClock(datetime(2026, 10, 10, 15, 0, tzinfo=timezone.utc)),
        revalidate, activate,
    )
    assert already_finished.considered == 0
    assert len(activation_keys) == (1 if crash_point == "before_activation" else 2)


def test_f02_interrupted_firing_stale_revalidation_blocks_without_activation() -> None:
    from scrubbots_content_pipeline.m17_release_controls import DueRevalidationResult

    _candidate, scheduled = _f02_scheduled_intent("f02-stale-recovery")
    store = SQLiteLocalProvider(sqlite3.connect(":memory:"))
    assert store.append_revision(scheduled, expected_revision_sha256=None)

    def interrupt_during_revalidation(_revision):
        raise SimulatedProcessInterruption()

    with pytest.raises(SimulatedProcessInterruption):
        run_due(
            store, FixedClock(datetime(2026, 10, 10, 15, 0, tzinfo=timezone.utc)),
            interrupt_during_revalidation,
            lambda _revision, *, idempotency_key: pytest.fail("interrupted before activation"),
        )

    blocked = run_due(
        store, FixedClock(datetime(2026, 10, 10, 15, 0, tzinfo=timezone.utc)),
        lambda _revision: DueRevalidationResult(True, False, True, True),
        lambda _revision, *, idempotency_key: pytest.fail("stale recovery must not activate"),
    )
    assert blocked.rejected == ((scheduled.schedule_id, "DUE_REVALIDATION_REJECTED"),)
    assert store.schedule_heads()[scheduled.schedule_id].state is ScheduleState.BLOCKED
    terminal = run_due(
        store, FixedClock(datetime(2026, 10, 10, 15, 0, tzinfo=timezone.utc)),
        lambda _revision: pytest.fail("terminal blocked schedule must not revalidate"),
        lambda _revision, *, idempotency_key: pytest.fail("terminal blocked schedule must not activate"),
    )
    assert terminal.considered == 0
