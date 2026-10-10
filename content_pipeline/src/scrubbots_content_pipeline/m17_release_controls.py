"""Provider-neutral rollback, disable, schedule and receipt contracts for M17.

This module prepares immutable successor manifests and durable control intents.
It never writes a live manifest. Final activation remains owned by the canonical
CP03 production activation path after its current-main replay and approval gates.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Protocol
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .config import Environment
from .compatibility import check_app_content_compatibility
from .current_main_replay import CurrentMainReplayReceipt, REPOSITORY
from .manifest_history import (
    ManifestHistoryRecord,
    ManifestHistoryV1,
    append_manifest_history,
    verify_manifest_history,
)
from .manifest_parser import parse_content_manifest_v1
from .manifest_v1 import ContentManifestV1
from .provider import ProviderObjectBytesResult, ProviderResultCategory

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_ISO_OFFSET = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:Z|[+-][0-9]{2}:[0-9]{2})$")
_CONTROL_OBJECT_KEY = re.compile(r"^control-candidates/[a-z0-9][a-z0-9._-]{0,63}(?:/[a-z0-9][a-z0-9._-]{0,63})*\.json$")
_ZONE_ID = re.compile(r"^[A-Za-z0-9_+-]+(?:/[A-Za-z0-9_+-]+)*$")


class ReleaseControlError(ValueError):
    """Fail-closed M17 control operation with a stable reason code."""

    def __init__(self, reason_code: str) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code


class ControlAction(StrEnum):
    ROLLBACK = "ROLLBACK"
    DISABLE = "DISABLE"
    REENABLE = "REENABLE"


class ReceiptOperation(StrEnum):
    PUBLISH = "PUBLISH"
    ROLLBACK = "ROLLBACK"
    DISABLE = "DISABLE"
    REENABLE = "REENABLE"
    SCHEDULE = "SCHEDULE"
    CANCEL_SCHEDULE = "CANCEL_SCHEDULE"


class ScheduleState(StrEnum):
    SCHEDULED = "SCHEDULED"
    CANCELLED = "CANCELLED"
    SUPERSEDED = "SUPERSEDED"
    FIRING = "FIRING"
    FIRED = "FIRED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True, slots=True)
class BoundOwnerApproval:
    """Approval bound to one exact action, target, active state and successor."""

    approval_id: str
    actor_ref: str
    action: ControlAction
    target_id: str
    expected_current_version: int
    expected_current_sha256: str
    new_content_version: int
    candidate_manifest_sha256: str

    def valid_for(self, *, action: ControlAction, target_id: str, current_version: int,
                  current_sha256: str, new_version: int, candidate_sha256: str) -> bool:
        return (
            isinstance(self.approval_id, str) and bool(_SAFE_ID.fullmatch(self.approval_id))
            and isinstance(self.actor_ref, str) and bool(_SAFE_ID.fullmatch(self.actor_ref))
            and self.action is action and self.target_id == target_id
            and type(self.expected_current_version) is int and self.expected_current_version == current_version
            and isinstance(self.expected_current_sha256, str) and _SHA256.fullmatch(self.expected_current_sha256)
            and self.expected_current_sha256 == current_sha256
            and type(self.new_content_version) is int and self.new_content_version == new_version
            and isinstance(self.candidate_manifest_sha256, str)
            and _SHA256.fullmatch(self.candidate_manifest_sha256)
            and self.candidate_manifest_sha256 == candidate_sha256
        )


@dataclass(frozen=True, slots=True)
class VerifiedKnownGood:
    record: ManifestHistoryRecord
    manifest: ContentManifestV1
    pack_bytes: tuple[tuple[str, bytes], ...]
    replay_receipt: CurrentMainReplayReceipt


class ExactObjectReader(Protocol):
    @property
    def identity(self) -> object: ...

    def read_object_bytes(self, environment: Environment, object_key: str) -> ProviderObjectBytesResult: ...


def select_known_good(
    history: ManifestHistoryV1,
    manifest_sha256: str,
    provider: ExactObjectReader,
    environment: Environment,
    replay: Callable[[bytes, Mapping[str, bytes]], CurrentMainReplayReceipt],
    *,
    current_game_version: str,
    supported_manifest_schema_versions: Mapping[str, Sequence[int] | range],
) -> VerifiedKnownGood:
    """Select only a complete, exact-byte, currently replay-proven history record."""
    checked = verify_manifest_history(history)
    if not checked.accepted:
        raise ReleaseControlError("INVALID_MANIFEST_HISTORY")
    if not isinstance(manifest_sha256, str) or not _SHA256.fullmatch(manifest_sha256):
        raise ReleaseControlError("INVALID_KNOWN_GOOD_IDENTITY")
    record = next((item for item in checked.verified_records if item.manifest_sha256 == manifest_sha256), None)
    if record is None:
        raise ReleaseControlError("KNOWN_GOOD_NOT_FOUND")
    try:
        manifest = parse_content_manifest_v1(record.manifest_bytes)
    except Exception as exc:
        raise ReleaseControlError("KNOWN_GOOD_MANIFEST_INVALID") from exc
    compatibility = check_app_content_compatibility(
        current_game_version=current_game_version,
        supported_manifest_schema_versions=supported_manifest_schema_versions,
        manifest_schema=manifest.schema,
        manifest_schema_version=manifest.schema_version,
        minimum_game_version=manifest.minimum_game_version,
    )
    if compatibility.compatible is not True:
        raise ReleaseControlError("KNOWN_GOOD_COMPATIBILITY_FAILED")
    if not _manifest_references_valid(manifest):
        raise ReleaseControlError("KNOWN_GOOD_REFERENCES_INVALID")
    exact_packs: list[tuple[str, bytes]] = []
    for pack in manifest.packs:
        try:
            result = provider.read_object_bytes(environment, pack.object_key)
        except Exception as exc:
            raise ReleaseControlError("KNOWN_GOOD_PACK_UNAVAILABLE") from exc
        raw = result.content_bytes if isinstance(result, ProviderObjectBytesResult) else None
        if (
            not isinstance(result, ProviderObjectBytesResult)
            or result.result_version != "1.0"
            or result.category is not ProviderResultCategory.SUCCESS
            or result.provider_id != getattr(getattr(provider, "identity", None), "provider_id", None)
            or result.environment is not environment or result.object_key != pack.object_key
            or type(raw) is not bytes or len(raw) != pack.byte_length
            or hashlib.sha256(raw).hexdigest() != pack.sha256
        ):
            raise ReleaseControlError("KNOWN_GOOD_PACK_INTEGRITY_FAILED")
        exact_packs.append((pack.pack_id, raw))
    try:
        receipt = replay(record.manifest_bytes, dict(exact_packs))
    except Exception as exc:
        raise ReleaseControlError("KNOWN_GOOD_CURRENT_MAIN_REPLAY_FAILED") from exc
    if (
        not isinstance(receipt, CurrentMainReplayReceipt) or receipt.accepted is not True
        or receipt.reason_code != "VERIFIED" or receipt.schema_version != "1.0"
        or receipt.game_repository != REPOSITORY or receipt.game_branch != "main"
        or not _GIT_SHA.fullmatch(receipt.game_commit)
        or receipt.manifest_sha256 != record.manifest_sha256
        or receipt.target_environment not in {"STAGING", "PRODUCTION"}
        or not _replay_matches_manifest(receipt, manifest)
    ):
        raise ReleaseControlError("KNOWN_GOOD_CURRENT_MAIN_REPLAY_FAILED")
    return VerifiedKnownGood(record, manifest, tuple(exact_packs), receipt)


@dataclass(frozen=True, slots=True)
class ReleaseCandidate:
    action: ControlAction
    target_id: str
    reason: str
    expected_current_version: int
    expected_current_sha256: str
    manifest_bytes: bytes
    manifest_sha256: str
    history: ManifestHistoryV1
    approval: BoundOwnerApproval


def prepare_rollback_candidate(
    current_manifest_bytes: bytes,
    history: ManifestHistoryV1,
    known_good: VerifiedKnownGood,
    *,
    target_id: str,
    reason: str,
    approval: BoundOwnerApproval,
    approval_check: Callable[[], BoundOwnerApproval | None],
    recorded_at_utc: str | datetime,
) -> ReleaseCandidate:
    """Prepare rollback bytes as a new version; never mutate the active provider."""
    current = _parse_current(current_manifest_bytes)
    if not _manifest_references_valid(current):
        raise ReleaseControlError("CURRENT_MANIFEST_REFERENCES_INVALID")
    if not isinstance(known_good, VerifiedKnownGood) or not any(
        item.record_sha256 == known_good.record.record_sha256
        and item.manifest_bytes == known_good.record.manifest_bytes
        for item in verify_manifest_history(history).verified_records
    ):
        raise ReleaseControlError("KNOWN_GOOD_NOT_IN_VERIFIED_HISTORY")
    restored = replace(known_good.manifest, content_version=current.content_version + 1)
    return _prepare_candidate(
        current_manifest_bytes, history, restored, ControlAction.ROLLBACK,
        target_id=target_id, reason=reason, approval=approval,
        approval_check=approval_check, recorded_at_utc=recorded_at_utc,
    )


def prepare_disable_candidate(
    current_manifest_bytes: bytes,
    history: ManifestHistoryV1,
    level_ids: Sequence[str],
    *,
    disabled: bool,
    target_id: str,
    reason: str,
    approval: BoundOwnerApproval,
    approval_check: Callable[[], BoundOwnerApproval | None],
    recorded_at_utc: str | datetime,
) -> ReleaseCandidate:
    """Prepare a precise disable/re-enable successor without rewriting packs."""
    current = _parse_current(current_manifest_bytes)
    if not _manifest_references_valid(current):
        raise ReleaseControlError("CURRENT_MANIFEST_REFERENCES_INVALID")
    if not isinstance(level_ids, (tuple, list)) or not level_ids:
        raise ReleaseControlError("INVALID_LEVEL_SELECTION")
    if any(not isinstance(item, str) or not _SAFE_ID.fullmatch(item) for item in level_ids):
        raise ReleaseControlError("INVALID_LEVEL_SELECTION")
    normalized = [item.casefold() for item in level_ids]
    if len(normalized) != len(set(normalized)):
        raise ReleaseControlError("DUPLICATE_LEVEL_SELECTION")
    declared = {level.level_id.casefold(): level.level_id for level in current.levels}
    if any(item not in declared for item in normalized):
        raise ReleaseControlError("UNKNOWN_LEVEL_ID")
    disabled_set = {item.casefold() for item in current.disabled_levels}
    if disabled and any(item in disabled_set for item in normalized):
        raise ReleaseControlError("LEVEL_ALREADY_DISABLED")
    if not disabled and any(item not in disabled_set for item in normalized):
        raise ReleaseControlError("LEVEL_NOT_DISABLED")
    updated = set(current.disabled_levels)
    if disabled:
        updated.update(declared[item] for item in normalized)
        action = ControlAction.DISABLE
    else:
        updated = {item for item in updated if item.casefold() not in set(normalized)}
        action = ControlAction.REENABLE
    desired = replace(current, content_version=current.content_version + 1,
                       disabled_levels=tuple(updated))
    return _prepare_candidate(
        current_manifest_bytes, history, desired, action, target_id=target_id, reason=reason,
        approval=approval, approval_check=approval_check, recorded_at_utc=recorded_at_utc,
    )


def _prepare_candidate(
    current_bytes: bytes, history: ManifestHistoryV1, desired: ContentManifestV1, action: ControlAction,
    *, target_id: str, reason: str, approval: BoundOwnerApproval,
    approval_check: Callable[[], BoundOwnerApproval | None], recorded_at_utc: str | datetime,
) -> ReleaseCandidate:
    current = _parse_current(current_bytes)
    valid_history = verify_manifest_history(history)
    current_sha = hashlib.sha256(current_bytes).hexdigest()
    if not valid_history.accepted or not valid_history.verified_records:
        raise ReleaseControlError("INVALID_MANIFEST_HISTORY")
    tip = valid_history.verified_records[-1]
    if tip.manifest_sha256 != current_sha or tip.content_version != current.content_version:
        raise ReleaseControlError("STALE_CURRENT_HISTORY")
    if not isinstance(target_id, str) or not _SAFE_ID.fullmatch(target_id):
        raise ReleaseControlError("INVALID_TARGET")
    if not isinstance(reason, str) or not reason.strip() or len(reason) > 2048:
        raise ReleaseControlError("REASON_REQUIRED")
    if desired.content_version != current.content_version + 1:
        raise ReleaseControlError("NON_MONOTONIC_SUCCESSOR")
    candidate_bytes = desired.to_json_bytes()
    candidate_sha = hashlib.sha256(candidate_bytes).hexdigest()
    try:
        fresh = approval_check() if callable(approval_check) else None
    except Exception:
        fresh = None
    if not isinstance(approval, BoundOwnerApproval) or not approval.valid_for(
        action=action, target_id=target_id, current_version=current.content_version,
        current_sha256=current_sha, new_version=desired.content_version, candidate_sha256=candidate_sha,
    ) or fresh != approval:
        raise ReleaseControlError("OWNER_APPROVAL_SCOPE_MISMATCH")
    try:
        successor_history = append_manifest_history(history, candidate_bytes, recorded_at_utc=recorded_at_utc)
    except Exception as exc:
        raise ReleaseControlError("HISTORY_APPEND_REJECTED") from exc
    return ReleaseCandidate(action, target_id, reason.strip(), current.content_version, current_sha,
                            candidate_bytes, candidate_sha, successor_history, approval)


def _parse_current(raw: bytes) -> ContentManifestV1:
    try:
        return parse_content_manifest_v1(raw)
    except Exception as exc:
        raise ReleaseControlError("INVALID_CURRENT_MANIFEST") from exc


def _manifest_references_valid(manifest: ContentManifestV1) -> bool:
    packs = {item.pack_id.casefold() for item in manifest.packs}
    levels = {item.level_id.casefold() for item in manifest.levels}
    if any(item.pack_id.casefold() not in packs for item in manifest.levels):
        return False
    if any(item.casefold() not in levels for item in manifest.disabled_levels):
        return False
    for schedule in manifest.schedules:
        available = packs if schedule.target_kind == "pack" else levels
        if schedule.target_id.casefold() not in available:
            return False
    return True


def _replay_matches_manifest(receipt: CurrentMainReplayReceipt, manifest: ContentManifestV1) -> bool:
    rows = receipt.pack_results
    expected_by_pack: dict[str, set[str]] = {}
    for level in manifest.levels:
        expected_by_pack.setdefault(level.pack_id, set()).add(level.level_id)
    if not isinstance(rows, tuple) or len(rows) != len(manifest.packs):
        return False
    observed: dict[str, object] = {}
    for row in rows:
        if not isinstance(row, Mapping) or not isinstance(row.get("pack_id"), str):
            return False
        pack_id = str(row["pack_id"])
        if pack_id in observed:
            return False
        observed[pack_id] = row
    if set(observed) != {pack.pack_id for pack in manifest.packs}:
        return False
    for pack in manifest.packs:
        row = observed[pack.pack_id]
        if row.get("pack_sha256") != pack.sha256:
            return False
        levels = row.get("levels")
        if not isinstance(levels, list):
            return False
        by_level = {item.get("level_id"): item for item in levels if isinstance(item, Mapping)}
        if len(by_level) != len(levels) or set(by_level) != expected_by_pack.get(pack.pack_id, set()):
            return False
        if any(not (
            item.get("accepted") is True and item.get("solver_status") == "SOLVED"
            and item.get("replay_solved") is True and item.get("unresolved") == 0
        ) for item in by_level.values()):
            return False
    return True


@dataclass(frozen=True, slots=True)
class ScheduleInstant:
    source_iso8601: str
    zone_id: str
    fold: int
    utc_iso8601: str


@dataclass(frozen=True, slots=True)
class ScheduleVerification:
    """Candidate-bound pre-schedule checks from canonical CP03/CPX verification."""

    candidate_manifest_sha256: str
    approval_id: str
    schema_valid: bool
    compatible: bool
    pack_hashes_verified: tuple[tuple[str, str, int], ...]
    current_main_replay: CurrentMainReplayReceipt

    def valid_for(self, candidate: ReleaseCandidate) -> bool:
        manifest = _parse_current(candidate.manifest_bytes)
        expected_packs = tuple(sorted((item.pack_id, item.sha256, item.byte_length)
                                      for item in manifest.packs))
        replay = self.current_main_replay
        return (
            self.candidate_manifest_sha256 == candidate.manifest_sha256
            and self.approval_id == candidate.approval.approval_id
            and self.schema_valid is True and self.compatible is True
            and tuple(sorted(self.pack_hashes_verified)) == expected_packs
            and isinstance(replay, CurrentMainReplayReceipt) and replay.accepted is True
            and replay.game_repository == REPOSITORY and replay.game_branch == "main"
            and replay.reason_code == "VERIFIED" and replay.schema_version == "1.0"
            and _GIT_SHA.fullmatch(replay.game_commit) is not None
            and replay.manifest_sha256 == candidate.manifest_sha256
            and _replay_matches_manifest(replay, manifest)
        )


def normalize_schedule_instant(source_iso8601: str, zone_id: str) -> ScheduleInstant:
    """Validate an offset-aware ISO instant against an IANA zone and DST rules."""
    if (not isinstance(source_iso8601, str) or not _ISO_OFFSET.fullmatch(source_iso8601)
            or not isinstance(zone_id, str) or len(source_iso8601) > 64
            or len(zone_id) > 128 or not _ZONE_ID.fullmatch(zone_id)):
        raise ReleaseControlError("INVALID_SCHEDULE_TIME")
    try:
        source = datetime.fromisoformat(source_iso8601)
        zone = ZoneInfo(zone_id)
    except (ValueError, ZoneInfoNotFoundError) as exc:
        raise ReleaseControlError("INVALID_SCHEDULE_TIME") from exc
    if source.tzinfo is None or source.utcoffset() is None or source.microsecond:
        raise ReleaseControlError("TIMEZONE_OFFSET_REQUIRED")
    wall = source.replace(tzinfo=None)
    candidates: list[tuple[int, datetime]] = []
    for fold in (0, 1):
        local = wall.replace(tzinfo=zone, fold=fold)
        round_trip = local.astimezone(timezone.utc).astimezone(zone)
        if round_trip.replace(tzinfo=None) == wall and round_trip.utcoffset() == local.utcoffset():
            candidates.append((fold, local))
    if not candidates:
        raise ReleaseControlError("NONEXISTENT_LOCAL_TIME")
    matches = [(fold, local) for fold, local in candidates if local.utcoffset() == source.utcoffset()]
    distinct_offsets = {local.utcoffset() for _, local in candidates}
    if len(distinct_offsets) > 1 and len(matches) > 1:
        raise ReleaseControlError("DST_FOLD_OFFSET_REQUIRED")
    if not matches:
        raise ReleaseControlError("TIMEZONE_OFFSET_MISMATCH")
    fold, local = matches[0]
    utc = local.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return ScheduleInstant(source_iso8601, zone_id, fold, utc)


@dataclass(frozen=True, slots=True)
class ScheduleRevision:
    schedule_id: str
    revision: int
    state: ScheduleState
    candidate_object_key: str
    candidate_manifest_sha256: str
    content_version: int
    expected_current_sha256: str
    expected_current_version: int
    target_id: str
    action: ControlAction
    approval_id: str
    scheduled_at: ScheduleInstant
    actor_ref: str
    previous_revision_sha256: str | None
    revision_sha256: str


def validate_schedule_transition(previous: ScheduleRevision | None, new: ScheduleRevision) -> bool:
    """Check one immutable schedule append and its only legal state transitions."""
    if not isinstance(new, ScheduleRevision):
        return False
    if previous is None:
        return new.revision == 1 and new.previous_revision_sha256 is None and new.state is ScheduleState.SCHEDULED
    if (
        not isinstance(previous, ScheduleRevision) or new.schedule_id != previous.schedule_id
        or new.revision != previous.revision + 1
        or new.previous_revision_sha256 != previous.revision_sha256
    ):
        return False
    allowed = {
        ScheduleState.SCHEDULED: {ScheduleState.SCHEDULED, ScheduleState.CANCELLED,
                                  ScheduleState.SUPERSEDED, ScheduleState.FIRING},
        ScheduleState.FIRING: {ScheduleState.FIRED, ScheduleState.BLOCKED},
    }
    return new.state in allowed.get(previous.state, set())


def create_schedule_revision(
    candidate: ReleaseCandidate,
    *,
    schedule_id: str,
    candidate_object_key: str,
    scheduled_at: ScheduleInstant,
    actor_ref: str,
    clock: "TrustedClock",
    verification: ScheduleVerification,
) -> ScheduleRevision:
    """Create a future schedule only for an exact prepared candidate and approval."""
    if not isinstance(candidate, ReleaseCandidate) or not isinstance(verification, ScheduleVerification):
        raise ReleaseControlError("VERIFIED_CANDIDATE_REQUIRED")
    if not verification.valid_for(candidate):
        raise ReleaseControlError("CANDIDATE_VERIFICATION_MISMATCH")
    authority = getattr(clock, "authority_id", None)
    now = clock.now_utc() if isinstance(authority, str) and _SAFE_ID.fullmatch(authority) else None
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise ReleaseControlError("TRUSTED_CLOCK_REQUIRED")
    if not isinstance(scheduled_at, ScheduleInstant):
        raise ReleaseControlError("INVALID_SCHEDULE_TIME")
    try:
        normalized_schedule = normalize_schedule_instant(scheduled_at.source_iso8601, scheduled_at.zone_id)
    except ReleaseControlError as exc:
        raise ReleaseControlError("INVALID_SCHEDULE_TIME") from exc
    if normalized_schedule != scheduled_at:
        raise ReleaseControlError("INVALID_SCHEDULE_TIME")
    due = datetime.strptime(scheduled_at.utc_iso8601, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    if due <= now.astimezone(timezone.utc):
        raise ReleaseControlError("SCHEDULE_MUST_BE_FUTURE")
    if hashlib.sha256(candidate.manifest_bytes).hexdigest() != candidate.manifest_sha256:
        raise ReleaseControlError("CANDIDATE_HASH_MISMATCH")
    if not candidate.approval.valid_for(
        action=candidate.action, target_id=candidate.target_id,
        current_version=candidate.expected_current_version,
        current_sha256=candidate.expected_current_sha256,
        new_version=candidate.expected_current_version + 1,
        candidate_sha256=candidate.manifest_sha256,
    ):
        raise ReleaseControlError("OWNER_APPROVAL_SCOPE_MISMATCH")
    return make_schedule_revision(
        schedule_id=schedule_id, revision=1, state=ScheduleState.SCHEDULED,
        candidate_object_key=candidate_object_key,
        candidate_manifest_sha256=candidate.manifest_sha256,
        content_version=candidate.expected_current_version + 1,
        expected_current_sha256=candidate.expected_current_sha256,
        expected_current_version=candidate.expected_current_version,
        target_id=candidate.target_id, action=candidate.action,
        approval_id=candidate.approval.approval_id, scheduled_at=scheduled_at,
        actor_ref=actor_ref, previous_revision_sha256=None,
    )


def cancel_schedule(previous: ScheduleRevision, *, actor_ref: str) -> ScheduleRevision:
    """Append a cancel revision; durable storage must CAS against the prior digest."""
    if not isinstance(previous, ScheduleRevision) or previous.state is not ScheduleState.SCHEDULED:
        raise ReleaseControlError("SCHEDULE_NOT_EDITABLE")
    return make_schedule_revision(
        schedule_id=previous.schedule_id, revision=previous.revision + 1,
        state=ScheduleState.CANCELLED, candidate_object_key=previous.candidate_object_key,
        candidate_manifest_sha256=previous.candidate_manifest_sha256,
        content_version=previous.content_version,
        expected_current_sha256=previous.expected_current_sha256,
        expected_current_version=previous.expected_current_version,
        target_id=previous.target_id, action=previous.action,
        approval_id=previous.approval_id, scheduled_at=previous.scheduled_at,
        actor_ref=actor_ref, previous_revision_sha256=previous.revision_sha256,
    )


def edit_schedule(
    previous: ScheduleRevision,
    candidate: ReleaseCandidate,
    *,
    candidate_object_key: str,
    scheduled_at: ScheduleInstant,
    actor_ref: str,
    clock: "TrustedClock",
    verification: ScheduleVerification,
) -> ScheduleRevision:
    """Append a replacement intent under the same schedule identity and revision chain."""
    if not isinstance(previous, ScheduleRevision) or previous.state is not ScheduleState.SCHEDULED:
        raise ReleaseControlError("SCHEDULE_NOT_EDITABLE")
    fresh = create_schedule_revision(
        candidate, schedule_id=previous.schedule_id,
        candidate_object_key=candidate_object_key, scheduled_at=scheduled_at,
        actor_ref=actor_ref, clock=clock, verification=verification,
    )
    return make_schedule_revision(
        schedule_id=previous.schedule_id, revision=previous.revision + 1,
        state=ScheduleState.SCHEDULED, candidate_object_key=fresh.candidate_object_key,
        candidate_manifest_sha256=fresh.candidate_manifest_sha256,
        content_version=fresh.content_version,
        expected_current_sha256=fresh.expected_current_sha256,
        expected_current_version=fresh.expected_current_version,
        target_id=fresh.target_id, action=fresh.action, approval_id=fresh.approval_id,
        scheduled_at=fresh.scheduled_at, actor_ref=actor_ref,
        previous_revision_sha256=previous.revision_sha256,
    )


def supersede_schedule(previous: ScheduleRevision, *, actor_ref: str) -> ScheduleRevision:
    """Append a terminal superseded revision before an operator creates a replacement ID."""
    if not isinstance(previous, ScheduleRevision) or previous.state is not ScheduleState.SCHEDULED:
        raise ReleaseControlError("SCHEDULE_NOT_EDITABLE")
    return make_schedule_revision(
        schedule_id=previous.schedule_id, revision=previous.revision + 1,
        state=ScheduleState.SUPERSEDED, candidate_object_key=previous.candidate_object_key,
        candidate_manifest_sha256=previous.candidate_manifest_sha256,
        content_version=previous.content_version,
        expected_current_sha256=previous.expected_current_sha256,
        expected_current_version=previous.expected_current_version,
        target_id=previous.target_id, action=previous.action,
        approval_id=previous.approval_id, scheduled_at=previous.scheduled_at,
        actor_ref=actor_ref, previous_revision_sha256=previous.revision_sha256,
    )


def make_schedule_revision(
    *, schedule_id: str, revision: int, state: ScheduleState, candidate_object_key: str,
    candidate_manifest_sha256: str, content_version: int, expected_current_sha256: str,
    expected_current_version: int, target_id: str, action: ControlAction, approval_id: str,
    scheduled_at: ScheduleInstant, actor_ref: str, previous_revision_sha256: str | None,
) -> ScheduleRevision:
    if not isinstance(state, ScheduleState) or not isinstance(action, ControlAction) or not isinstance(scheduled_at, ScheduleInstant):
        raise ReleaseControlError("INVALID_SCHEDULE_REVISION")
    if normalize_schedule_instant(scheduled_at.source_iso8601, scheduled_at.zone_id) != scheduled_at:
        raise ReleaseControlError("INVALID_SCHEDULE_REVISION")
    fields = {
        "action": action.value, "actor_ref": actor_ref, "approval_id": approval_id,
        "candidate_manifest_sha256": candidate_manifest_sha256,
        "candidate_object_key": candidate_object_key, "content_version": content_version,
        "expected_current_sha256": expected_current_sha256,
        "expected_current_version": expected_current_version,
        "previous_revision_sha256": previous_revision_sha256,
        "revision": revision, "schedule_id": schedule_id,
        "scheduled_at": {"fold": scheduled_at.fold, "source_iso8601": scheduled_at.source_iso8601,
                          "utc_iso8601": scheduled_at.utc_iso8601, "zone_id": scheduled_at.zone_id},
        "state": state.value, "target_id": target_id,
    }
    if (
        not isinstance(schedule_id, str) or not _SAFE_ID.fullmatch(schedule_id)
        or type(revision) is not int or revision < 1
        or not isinstance(actor_ref, str) or not _SAFE_ID.fullmatch(actor_ref)
        or not isinstance(approval_id, str) or not _SAFE_ID.fullmatch(approval_id)
        or not isinstance(target_id, str) or not _SAFE_ID.fullmatch(target_id)
        or not isinstance(candidate_object_key, str) or not _CONTROL_OBJECT_KEY.fullmatch(candidate_object_key)
        or not isinstance(candidate_manifest_sha256, str) or not _SHA256.fullmatch(candidate_manifest_sha256)
        or not isinstance(expected_current_sha256, str) or not _SHA256.fullmatch(expected_current_sha256)
        or type(content_version) is not int or content_version < 2
        or type(expected_current_version) is not int or expected_current_version < 1
        or content_version <= expected_current_version
        or (previous_revision_sha256 is not None and (
            not isinstance(previous_revision_sha256, str) or not _SHA256.fullmatch(previous_revision_sha256)
        ))
    ):
        raise ReleaseControlError("INVALID_SCHEDULE_REVISION")
    digest = hashlib.sha256(_canonical_json(fields)).hexdigest()
    return ScheduleRevision(schedule_id, revision, state, candidate_object_key,
                            candidate_manifest_sha256, content_version, expected_current_sha256,
                            expected_current_version, target_id, action, approval_id, scheduled_at,
                            actor_ref, previous_revision_sha256, digest)


def serialize_schedule_revision(revision: ScheduleRevision) -> bytes:
    """Deterministically serialize one immutable, hash-chained schedule event."""
    if not isinstance(revision, ScheduleRevision):
        raise ReleaseControlError("INVALID_SCHEDULE_REVISION")
    payload = _schedule_fields(revision)
    if hashlib.sha256(_canonical_json(payload)).hexdigest() != revision.revision_sha256:
        raise ReleaseControlError("SCHEDULE_REVISION_DIGEST_MISMATCH")
    payload["revision_sha256"] = revision.revision_sha256
    return _canonical_json(payload)


def parse_schedule_revision(raw: bytes) -> ScheduleRevision:
    """Parse one strict schedule record and verify its digest and timezone binding."""
    if type(raw) is not bytes:
        raise ReleaseControlError("INVALID_SCHEDULE_REVISION")
    try:
        value = json.loads(raw.decode("utf-8"))
        expected = {
            "action", "actor_ref", "approval_id", "candidate_manifest_sha256",
            "candidate_object_key", "content_version", "expected_current_sha256",
            "expected_current_version", "previous_revision_sha256", "revision", "schedule_id",
            "scheduled_at", "state", "target_id", "revision_sha256",
        }
        if not isinstance(value, dict) or set(value) != expected:
            raise ValueError
        when = value["scheduled_at"]
        if not isinstance(when, dict) or set(when) != {"fold", "source_iso8601", "utc_iso8601", "zone_id"}:
            raise ValueError
        instant = normalize_schedule_instant(when["source_iso8601"], when["zone_id"])
        if instant.fold != when["fold"] or instant.utc_iso8601 != when["utc_iso8601"]:
            raise ValueError
        item = make_schedule_revision(
            schedule_id=value["schedule_id"], revision=value["revision"],
            state=ScheduleState(value["state"]), candidate_object_key=value["candidate_object_key"],
            candidate_manifest_sha256=value["candidate_manifest_sha256"],
            content_version=value["content_version"],
            expected_current_sha256=value["expected_current_sha256"],
            expected_current_version=value["expected_current_version"], target_id=value["target_id"],
            action=ControlAction(value["action"]), approval_id=value["approval_id"],
            scheduled_at=instant, actor_ref=value["actor_ref"],
            previous_revision_sha256=value["previous_revision_sha256"],
        )
        if value["revision_sha256"] != item.revision_sha256 or serialize_schedule_revision(item) != raw:
            raise ValueError
        return item
    except (KeyError, TypeError, ValueError, UnicodeDecodeError) as exc:
        raise ReleaseControlError("INVALID_SCHEDULE_REVISION") from exc


def _schedule_fields(revision: ScheduleRevision) -> dict[str, object]:
    return {
        "action": revision.action.value, "actor_ref": revision.actor_ref,
        "approval_id": revision.approval_id,
        "candidate_manifest_sha256": revision.candidate_manifest_sha256,
        "candidate_object_key": revision.candidate_object_key,
        "content_version": revision.content_version,
        "expected_current_sha256": revision.expected_current_sha256,
        "expected_current_version": revision.expected_current_version,
        "previous_revision_sha256": revision.previous_revision_sha256,
        "revision": revision.revision, "schedule_id": revision.schedule_id,
        "scheduled_at": {"fold": revision.scheduled_at.fold,
                          "source_iso8601": revision.scheduled_at.source_iso8601,
                          "utc_iso8601": revision.scheduled_at.utc_iso8601,
                          "zone_id": revision.scheduled_at.zone_id},
        "state": revision.state.value, "target_id": revision.target_id,
    }


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


@dataclass(frozen=True, slots=True)
class ControlReceipt:
    actor_ref: str
    operation: str
    occurred_at_utc: str
    target_id: str
    current_version: int
    next_version: int
    prior_manifest_sha256: str
    new_manifest_sha256: str
    pack_hashes: tuple[tuple[str, str], ...]
    approval_id: str
    provider_record_sha256: str
    outcome: str
    report_sha256: str

    def to_dict(self) -> dict[str, object]:
        return {
            "actor_ref": self.actor_ref, "approval_id": self.approval_id,
            "current_version": self.current_version, "new_manifest_sha256": self.new_manifest_sha256,
            "next_version": self.next_version, "occurred_at_utc": self.occurred_at_utc,
            "operation": self.operation, "outcome": self.outcome,
            "pack_hashes": [{"pack_id": key, "sha256": value} for key, value in self.pack_hashes],
            "prior_manifest_sha256": self.prior_manifest_sha256,
            "provider_record_sha256": self.provider_record_sha256,
            "report_sha256": self.report_sha256, "target_id": self.target_id,
        }


def make_control_receipt(
    *, actor_ref: str, operation: ControlAction | ReceiptOperation, occurred_at_utc: str, target_id: str,
    current_version: int, next_version: int, prior_manifest_sha256: str,
    new_manifest_sha256: str, pack_hashes: Sequence[tuple[str, str]], approval_id: str,
    provider_record_sha256: str, outcome: str,
) -> ControlReceipt:
    try:
        operation_value = operation.value
        ReceiptOperation(operation_value)
    except (AttributeError, ValueError) as exc:
        raise ReleaseControlError("INVALID_RECEIPT_OPERATION") from exc
    fields: dict[str, object] = {
        "actor_ref": actor_ref, "approval_id": approval_id,
        "current_version": current_version, "new_manifest_sha256": new_manifest_sha256,
        "next_version": next_version, "occurred_at_utc": occurred_at_utc,
        "operation": operation_value, "outcome": outcome,
        "pack_hashes": [{"pack_id": key, "sha256": value} for key, value in sorted(pack_hashes)],
        "prior_manifest_sha256": prior_manifest_sha256,
        "provider_record_sha256": provider_record_sha256, "target_id": target_id,
    }
    _validate_receipt_fields(fields)
    digest = hashlib.sha256(_canonical_json(fields)).hexdigest()
    return ControlReceipt(actor_ref, operation_value, occurred_at_utc, target_id, current_version,
                          next_version, prior_manifest_sha256, new_manifest_sha256,
                          tuple(sorted(pack_hashes)), approval_id, provider_record_sha256, outcome, digest)


def serialize_control_receipt(receipt: ControlReceipt) -> bytes:
    fields = receipt.to_dict()
    digest = fields.pop("report_sha256")
    if hashlib.sha256(_canonical_json(fields)).hexdigest() != digest:
        raise ReleaseControlError("REPORT_DIGEST_MISMATCH")
    fields["report_sha256"] = digest
    return _canonical_json(fields)


def render_control_receipt(receipt: ControlReceipt) -> str:
    """Render a stable human-readable summary from the same validated receipt."""
    serialize_control_receipt(receipt)
    return (
        f"{receipt.operation} {receipt.outcome}: {receipt.current_version} -> {receipt.next_version}; "
        f"target={receipt.target_id}; manifest={receipt.new_manifest_sha256}; "
        f"approval={receipt.approval_id}; report={receipt.report_sha256}\n"
    )


def _validate_receipt_fields(fields: Mapping[str, object]) -> None:
    try:
        when = datetime.strptime(str(fields["occurred_at_utc"]), "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ReleaseControlError("INVALID_RECEIPT_TIME") from exc
    if when.strftime("%Y-%m-%dT%H:%M:%SZ") != fields["occurred_at_utc"]:
        raise ReleaseControlError("INVALID_RECEIPT_TIME")
    for key in ("actor_ref", "target_id", "approval_id"):
        if not isinstance(fields.get(key), str) or not _SAFE_ID.fullmatch(str(fields[key])):
            raise ReleaseControlError("INVALID_RECEIPT_IDENTITY")
    if fields.get("operation") not in {item.value for item in ReceiptOperation}:
        raise ReleaseControlError("INVALID_RECEIPT_OPERATION")
    if not isinstance(fields.get("outcome"), str) or not _SAFE_ID.fullmatch(str(fields["outcome"])):
        raise ReleaseControlError("INVALID_RECEIPT_OUTCOME")
    for key in ("prior_manifest_sha256", "new_manifest_sha256", "provider_record_sha256"):
        if not isinstance(fields.get(key), str) or not _SHA256.fullmatch(str(fields[key])):
            raise ReleaseControlError("INVALID_RECEIPT_DIGEST")
    if type(fields.get("current_version")) is not int or type(fields.get("next_version")) is not int:
        raise ReleaseControlError("INVALID_RECEIPT_VERSION")
    if int(fields["current_version"]) < 1 or int(fields["next_version"]) <= int(fields["current_version"]):
        raise ReleaseControlError("NON_MONOTONIC_RECEIPT")
    packs = fields.get("pack_hashes")
    if not isinstance(packs, list):
        raise ReleaseControlError("INVALID_RECEIPT_PACKS")
    seen_pack_ids: set[str] = set()
    for item in packs:
        if (not isinstance(item, Mapping) or not isinstance(item.get("pack_id"), str)
                or not _SAFE_ID.fullmatch(str(item["pack_id"]))
                or not isinstance(item.get("sha256"), str) or not _SHA256.fullmatch(str(item["sha256"]))
                or item["pack_id"] in seen_pack_ids):
            raise ReleaseControlError("INVALID_RECEIPT_PACKS")
        seen_pack_ids.add(str(item["pack_id"]))


@dataclass(frozen=True, slots=True)
class WeeklyAcceptedBatch:
    batch_id: str
    week_id: str
    accepted_candidate_ids: tuple[str, ...]
    source_sha256: str
    supply_sha256: str
    replay_sha256: str
    immutable_identity_sha256: str


def make_weekly_accepted_batch(
    batch_id: str, week_id: str, accepted_candidate_ids: Sequence[str],
    source_sha256: str, supply_sha256: str, replay_sha256: str,
) -> WeeklyAcceptedBatch:
    if (
        not isinstance(batch_id, str) or not _SAFE_ID.fullmatch(batch_id)
        or not isinstance(week_id, str) or not _SAFE_ID.fullmatch(week_id)
        or not isinstance(accepted_candidate_ids, (tuple, list)) or not accepted_candidate_ids
        or any(not isinstance(item, str) or not _SAFE_ID.fullmatch(item) for item in accepted_candidate_ids)
        or len(set(accepted_candidate_ids)) != len(accepted_candidate_ids)
        or any(not _SHA256.fullmatch(item) for item in (source_sha256, supply_sha256, replay_sha256))
    ):
        raise ReleaseControlError("INVALID_WEEKLY_BATCH")
    identity = hashlib.sha256(_canonical_json({
        "accepted_candidate_ids": list(accepted_candidate_ids), "batch_id": batch_id,
        "replay_sha256": replay_sha256, "source_sha256": source_sha256,
        "supply_sha256": supply_sha256, "week_id": week_id,
    })).hexdigest()
    return WeeklyAcceptedBatch(batch_id, week_id, tuple(accepted_candidate_ids), source_sha256,
                               supply_sha256, replay_sha256, identity)


class ScheduleJournal(Protocol):
    """Durable append-only schedule heads with atomic compare-and-swap semantics."""

    def schedule_heads(self) -> Mapping[str, ScheduleRevision]: ...

    def append_revision(self, revision: ScheduleRevision, *, expected_revision_sha256: str | None) -> bool: ...

    def claim_due(self, schedule_id: str, *, expected_revision_sha256: str, claim_key: str) -> bool: ...

    def finish_due(self, schedule_id: str, *, expected_revision_sha256: str,
                   state: ScheduleState, claim_key: str) -> bool: ...


class TrustedClock(Protocol):
    authority_id: str

    def now_utc(self) -> datetime: ...


class CandidateRevalidator(Protocol):
    def __call__(self, revision: ScheduleRevision) -> DueRevalidationResult: ...


class CandidateActivator(Protocol):
    """Idempotent activation keyed by durable claim identity.

    Implementations must deduplicate activation effects by ``idempotency_key``.
    A false result or raised exception may mean the remote acknowledgment was
    lost; callers keep the schedule FIRING and may retry with the same key.
    """

    def __call__(self, revision: ScheduleRevision, *, idempotency_key: str) -> bool: ...


@dataclass(frozen=True, slots=True)
class DueRunResult:
    considered: int
    claimed: tuple[str, ...]
    activated: tuple[str, ...]
    rejected: tuple[tuple[str, str], ...]
    clock_authority: str


@dataclass(frozen=True, slots=True)
class DueRevalidationResult:
    """Explicit due-time checks repeated immediately before activation."""

    current_state_and_cas: bool
    approval_scope_and_revocation: bool
    packs_hash_schema_and_compatibility: bool
    current_main_solved_replay: bool

    @property
    def accepted(self) -> bool:
        return all((self.current_state_and_cas, self.approval_scope_and_revocation,
                    self.packs_hash_schema_and_compatibility, self.current_main_solved_replay))


def run_due(
    journal: ScheduleJournal, clock: TrustedClock, revalidate: CandidateRevalidator,
    activate: CandidateActivator,
) -> DueRunResult:
    """Deterministically claim due intents and revalidate immediately before activation."""
    if not isinstance(getattr(clock, "authority_id", None), str) or not _SAFE_ID.fullmatch(clock.authority_id):
        raise ReleaseControlError("TRUSTED_CLOCK_REQUIRED")
    now = clock.now_utc()
    if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
        raise ReleaseControlError("TRUSTED_CLOCK_INVALID")
    now_utc = now.astimezone(timezone.utc)
    if now_utc.microsecond:
        raise ReleaseControlError("TRUSTED_CLOCK_PRECISION_INVALID")
    due = [item for item in journal.schedule_heads().values()
           if item.state in {ScheduleState.SCHEDULED, ScheduleState.FIRING}
           and datetime.strptime(item.scheduled_at.utc_iso8601, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) <= now_utc]
    claimed: list[str] = []
    activated: list[str] = []
    rejected: list[tuple[str, str]] = []
    for revision in sorted(due, key=lambda item: (item.scheduled_at.utc_iso8601, item.schedule_id)):
        # claim_due advances SCHEDULED revision N to FIRING revision N+1.
        # Reconstruct N on a resumed FIRING head so retries use the identity
        # already persisted by the original claim, including after uncertain
        # activation acknowledgments.
        claim_revision = revision.revision
        if revision.state is ScheduleState.FIRING:
            if revision.revision < 2:
                rejected.append((revision.schedule_id, "FIRING_REVISION_INVALID"))
                continue
            claim_revision -= 1
        claim_key = f"{revision.schedule_id}:{claim_revision}:{revision.candidate_manifest_sha256}"
        if not journal.claim_due(revision.schedule_id,
                                 expected_revision_sha256=revision.revision_sha256, claim_key=claim_key):
            rejected.append((revision.schedule_id, "SCHEDULE_CLAIM_CONFLICT"))
            continue
        claimed.append(revision.schedule_id)
        current = journal.schedule_heads().get(revision.schedule_id)
        if not isinstance(current, ScheduleRevision) or current.state is not ScheduleState.FIRING:
            rejected.append((revision.schedule_id, "SCHEDULE_CLAIM_STATE_INVALID"))
            continue
        try:
            checks = revalidate(current)
        except Exception:
            checks = None
        if not isinstance(checks, DueRevalidationResult) or checks.accepted is not True:
            journal.finish_due(revision.schedule_id, expected_revision_sha256=current.revision_sha256,
                               state=ScheduleState.BLOCKED, claim_key=claim_key)
            rejected.append((revision.schedule_id, "DUE_REVALIDATION_REJECTED"))
            continue
        try:
            success = activate(current, idempotency_key=claim_key)
        except Exception:
            success = False
        if success is True:
            if journal.finish_due(revision.schedule_id, expected_revision_sha256=current.revision_sha256,
                                  state=ScheduleState.FIRED, claim_key=claim_key):
                activated.append(revision.schedule_id)
            else:
                rejected.append((revision.schedule_id, "SCHEDULE_FINALIZE_CONFLICT"))
        else:
            rejected.append((revision.schedule_id, "ACTIVATION_NOT_CONFIRMED"))
    return DueRunResult(len(due), tuple(claimed), tuple(activated), tuple(rejected), clock.authority_id)


__all__ = [
    "BoundOwnerApproval", "CandidateActivator", "CandidateRevalidator", "ControlAction",
    "ControlReceipt", "DueRevalidationResult", "DueRunResult", "ExactObjectReader", "ReleaseCandidate",
    "ReceiptOperation", "ReleaseControlError", "ScheduleInstant", "ScheduleJournal", "ScheduleRevision", "ScheduleVerification",
    "ScheduleState", "TrustedClock", "VerifiedKnownGood", "WeeklyAcceptedBatch",
    "cancel_schedule", "create_schedule_revision", "edit_schedule", "make_control_receipt",
    "make_schedule_revision", "make_weekly_accepted_batch",
    "normalize_schedule_instant", "prepare_disable_candidate", "prepare_rollback_candidate",
    "parse_schedule_revision", "render_control_receipt", "run_due", "select_known_good",
    "serialize_control_receipt", "serialize_schedule_revision", "supersede_schedule",
    "validate_schedule_transition",
]
