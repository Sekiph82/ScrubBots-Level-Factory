"""LEGACY_NON_PRODUCTION: offline advisory-only telemetry calibration contracts for SB-LF09-004.

This module accepts already-produced gameplay evidence.  It does not collect
telemetry, contact a provider, mutate LevelData, or change the M04 result.
All timestamps used for retention are explicit inputs; no wall clock is read
while building a canonical report.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from enum import Enum
import hashlib
import json
import math
import re

from .difficulty_analysis import (
    ChallengeScoreResult,
    DifficultyAnalysis,
    LaneMappingResult,
)


TELEMETRY_POLICY_VERSION = "SB_LF09_004_ANALYTICS_DATA_POLICY_V01"
TELEMETRY_EVENT_SCHEMA = "scrubbots-telemetry-event"
TELEMETRY_SESSION_SCHEMA = "scrubbots-telemetry-session"
TELEMETRY_AGGREGATE_SCHEMA = "scrubbots-telemetry-aggregate"
TELEMETRY_REPORT_SCHEMA = "scrubbots-telemetry-calibration-report"
TELEMETRY_SCHEMA_VERSION = 1
TELEMETRY_EVENT_VERSION = 1
TELEMETRY_SESSION_VERSION = 1
TELEMETRY_AGGREGATE_VERSION = 1
TELEMETRY_REPORT_VERSION = 1
RAW_TELEMETRY_RETENTION_DAYS = 90
AGGREGATE_CALIBRATION_RETENTION_DAYS = 365
MINIMUM_VALID_SESSIONS = 100
M04_CALIBRATION_BINDING_VERSION = "M04_DIFFICULTY_V1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_PSEUDONYMOUS_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{7,127}$")
_UTC_SUFFIX = re.compile(r"Z$")


class TelemetryCalibrationError(ValueError):
    """Raised for malformed typed telemetry or an invalid M04 binding."""


class CalibrationDisposition(str, Enum):
    ADVISORY_READY = "ADVISORY_READY"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    UNAVAILABLE = "UNAVAILABLE"
    INCONCLUSIVE = "INCONCLUSIVE"
    ERROR = "ERROR"


class TelemetryEventKind(str, Enum):
    LEVEL_START = "LEVEL_START"
    WIN = "WIN"
    LOSS = "LOSS"
    RESTART = "RESTART"
    QUIT = "QUIT"
    ABANDON = "ABANDON"
    BOOSTER_USAGE = "BOOSTER_USAGE"


def _canonical_bytes(value: Mapping[str, object]) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(value: Mapping[str, object]) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _require_token(value: object, label: str, *, pseudonymous: bool = False) -> str:
    pattern = _PSEUDONYMOUS_ID if pseudonymous else _IDENTIFIER_PATTERN
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise TelemetryCalibrationError(f"{label} is not a permitted token")
    return value


def _require_digest(value: object, label: str) -> str:
    if type(value) is not str or _SHA256.fullmatch(value) is None:
        raise TelemetryCalibrationError(f"{label} must be a lowercase SHA-256")
    return value


def _utc_timestamp(value: object, label: str) -> str:
    if isinstance(value, datetime):
        selected = value
    elif type(value) is str:
        raw = value[:-1] + "+00:00" if _UTC_SUFFIX.search(value) else value
        try:
            selected = datetime.fromisoformat(raw)
        except ValueError as exc:
            raise TelemetryCalibrationError(f"{label} is not an ISO-8601 timestamp") from exc
    else:
        raise TelemetryCalibrationError(f"{label} must be an ISO-8601 timestamp")
    if selected.tzinfo is None or selected.utcoffset() is None:
        raise TelemetryCalibrationError(f"{label} must include a UTC offset")
    return selected.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _timestamp_value(value: str) -> datetime:
    return datetime.fromisoformat(value[:-1] + "+00:00")


def _as_of(value: object) -> datetime:
    return _timestamp_value(_utc_timestamp(value, "as_of"))


def _number(value: object, label: str, *, minimum: float = 0.0, maximum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise TelemetryCalibrationError(f"{label} must be finite")
    selected = float(value)
    if selected < minimum or (maximum is not None and selected > maximum):
        raise TelemetryCalibrationError(f"{label} is outside its policy bounds")
    return selected


def _count(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise TelemetryCalibrationError(f"{label} must be a non-negative integer")
    return value


@dataclass(frozen=True, slots=True)
class TelemetryEvent:
    kind: TelemetryEventKind | str
    occurred_at: str | datetime
    count: int = 1
    schema_version: int = TELEMETRY_EVENT_VERSION

    def __post_init__(self) -> None:
        try:
            kind = self.kind if isinstance(self.kind, TelemetryEventKind) else TelemetryEventKind(self.kind)
        except (TypeError, ValueError) as exc:
            raise TelemetryCalibrationError("telemetry event kind is not approved") from exc
        if type(self.schema_version) is not int or self.schema_version != TELEMETRY_EVENT_VERSION:
            raise TelemetryCalibrationError("unsupported telemetry event version")
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "occurred_at", _utc_timestamp(self.occurred_at, "event occurred_at"))
        if type(self.count) is not int or self.count < 1:
            raise TelemetryCalibrationError("event count must be a positive integer")

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": TELEMETRY_EVENT_SCHEMA, "version": self.schema_version, "kind": self.kind.value, "occurred_at": self.occurred_at, "count": self.count}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return _digest(self.canonical_dict())

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "TelemetryEvent":
        fields = {"schema", "version", "kind", "occurred_at", "count"}
        if not isinstance(payload, Mapping) or set(payload) != fields or payload["schema"] != TELEMETRY_EVENT_SCHEMA:
            raise TelemetryCalibrationError("telemetry event has unknown or unsupported fields")
        return cls(payload["kind"], payload["occurred_at"], payload["count"], payload["version"])


@dataclass(frozen=True, slots=True)
class TelemetrySession:
    """One privacy-safe gameplay session; raw identity never enters aggregates."""

    session_id: str
    level_id: str
    candidate_id: str | None
    game_version: str
    recorded_at: str | datetime
    events: tuple[TelemetryEvent, ...]
    attempt_count: int
    move_count: int
    completion_duration_ms: int | None
    challenge_score: float
    challenge_score_policy_version: str
    lane: str
    lane_mapping_policy_version: str
    cohort_version: str
    m04_analysis_digest: str
    challenge_score_digest: str
    lane_mapping_digest: str
    schema_version: int = TELEMETRY_SESSION_VERSION
    record_digest: str = ""

    def __post_init__(self) -> None:
        _require_token(self.session_id, "session_id", pseudonymous=True)
        _require_token(self.level_id, "level_id")
        if self.candidate_id is not None:
            _require_token(self.candidate_id, "candidate_id")
        _require_token(self.game_version, "game_version")
        _require_token(self.cohort_version, "cohort_version")
        if type(self.schema_version) is not int or self.schema_version != TELEMETRY_SESSION_VERSION:
            raise TelemetryCalibrationError("unsupported telemetry session version")
        object.__setattr__(self, "recorded_at", _utc_timestamp(self.recorded_at, "session recorded_at"))
        if type(self.events) is not tuple or any(not isinstance(event, TelemetryEvent) for event in self.events):
            raise TelemetryCalibrationError("session events must be an immutable tuple of approved events")
        if type(self.attempt_count) is not int or self.attempt_count < 1:
            raise TelemetryCalibrationError("attempt_count must be a positive integer")
        if type(self.move_count) is not int or self.move_count < 0:
            raise TelemetryCalibrationError("move_count must be a non-negative integer")
        if self.completion_duration_ms is not None and (type(self.completion_duration_ms) is not int or self.completion_duration_ms < 0):
            raise TelemetryCalibrationError("completion_duration_ms must be non-negative")
        object.__setattr__(self, "challenge_score", _number(self.challenge_score, "challenge_score", maximum=100.0))
        _require_token(self.challenge_score_policy_version, "challenge_score_policy_version")
        _require_token(self.lane, "lane")
        if self.lane not in {"EASY", "MEDIUM", "HARD", "VERY_HARD"}:
            raise TelemetryCalibrationError("lane is not an approved M04 lane")
        _require_token(self.lane_mapping_policy_version, "lane_mapping_policy_version")
        for value, label in ((self.m04_analysis_digest, "m04_analysis_digest"), (self.challenge_score_digest, "challenge_score_digest"), (self.lane_mapping_digest, "lane_mapping_digest")):
            _require_digest(value, label)
        expected = self._expected_digest()
        if self.record_digest and self.record_digest != expected:
            raise TelemetryCalibrationError("telemetry session digest does not match its immutable content")
        object.__setattr__(self, "record_digest", expected)

    def _identity_dict(self) -> dict[str, object]:
        return {"schema": TELEMETRY_SESSION_SCHEMA, "version": self.schema_version, "session_id": self.session_id, "level_id": self.level_id, "candidate_id": self.candidate_id, "game_version": self.game_version, "recorded_at": self.recorded_at, "events": [event.canonical_dict() for event in self.events], "attempt_count": self.attempt_count, "move_count": self.move_count, "completion_duration_ms": self.completion_duration_ms, "challenge_score": self.challenge_score, "challenge_score_policy_version": self.challenge_score_policy_version, "lane": self.lane, "lane_mapping_policy_version": self.lane_mapping_policy_version, "cohort_version": self.cohort_version, "m04_analysis_digest": self.m04_analysis_digest, "challenge_score_digest": self.challenge_score_digest, "lane_mapping_digest": self.lane_mapping_digest}

    def _expected_digest(self) -> str:
        return _digest(self._identity_dict())

    def canonical_dict(self) -> dict[str, object]:
        return {**self._identity_dict(), "record_digest": self.record_digest}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return self.record_digest

    @property
    def terminal_kind(self) -> TelemetryEventKind | None:
        terminal = [event.kind for event in self.events if event.kind in {TelemetryEventKind.WIN, TelemetryEventKind.LOSS, TelemetryEventKind.QUIT, TelemetryEventKind.ABANDON}]
        return terminal[0] if len(terminal) == 1 else None

    @property
    def restart_count(self) -> int:
        return sum(event.count for event in self.events if event.kind is TelemetryEventKind.RESTART)

    @property
    def booster_usage_count(self) -> int:
        return sum(event.count for event in self.events if event.kind is TelemetryEventKind.BOOSTER_USAGE)

    def is_valid_gameplay_session(self) -> bool:
        starts = [event for event in self.events if event.kind is TelemetryEventKind.LEVEL_START]
        terminal = self.terminal_kind
        return len(starts) == 1 and terminal is not None and self.attempt_count >= 1

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "TelemetrySession":
        fields = {"schema", "version", "session_id", "level_id", "candidate_id", "game_version", "recorded_at", "events", "attempt_count", "move_count", "completion_duration_ms", "challenge_score", "challenge_score_policy_version", "lane", "lane_mapping_policy_version", "cohort_version", "m04_analysis_digest", "challenge_score_digest", "lane_mapping_digest", "record_digest"}
        if not isinstance(payload, Mapping) or set(payload) != fields or payload["schema"] != TELEMETRY_SESSION_SCHEMA:
            raise TelemetryCalibrationError("telemetry session has unknown, prohibited, or missing fields")
        events = payload["events"]
        if type(events) is not list:
            raise TelemetryCalibrationError("telemetry session events must be a list in transport form")
        return cls(payload["session_id"], payload["level_id"], payload["candidate_id"], payload["game_version"], payload["recorded_at"], tuple(TelemetryEvent.from_dict(event) for event in events), payload["attempt_count"], payload["move_count"], payload["completion_duration_ms"], payload["challenge_score"], payload["challenge_score_policy_version"], payload["lane"], payload["lane_mapping_policy_version"], payload["cohort_version"], payload["m04_analysis_digest"], payload["challenge_score_digest"], payload["lane_mapping_digest"], payload["version"], payload["record_digest"])


@dataclass(frozen=True, slots=True)
class M04DifficultyBinding:
    """The exact accepted M04 identity carried into an advisory report."""

    analysis_digest: str
    level_metrics_digest: str
    challenge_score_digest: str
    challenge_score_policy_version: str
    lane_mapping_digest: str
    lane_mapping_policy_version: str
    challenge_score: float
    lane: str
    binding_version: str = M04_CALIBRATION_BINDING_VERSION

    def __post_init__(self) -> None:
        for value, label in ((self.analysis_digest, "analysis_digest"), (self.level_metrics_digest, "level_metrics_digest"), (self.challenge_score_digest, "challenge_score_digest"), (self.lane_mapping_digest, "lane_mapping_digest")):
            _require_digest(value, label)
        _require_token(self.challenge_score_policy_version, "challenge_score_policy_version")
        _require_token(self.lane_mapping_policy_version, "lane_mapping_policy_version")
        _require_token(self.binding_version, "binding_version")
        _number(self.challenge_score, "challenge_score", maximum=100.0)
        _require_token(self.lane, "lane")
        if self.lane not in {"EASY", "MEDIUM", "HARD", "VERY_HARD"}:
            raise TelemetryCalibrationError("M04 binding lane is malformed")

    @classmethod
    def from_results(cls, analysis: DifficultyAnalysis, score: ChallengeScoreResult, lane: LaneMappingResult) -> "M04DifficultyBinding":
        if not isinstance(analysis, DifficultyAnalysis) or not isinstance(score, ChallengeScoreResult) or not isinstance(lane, LaneMappingResult):
            raise TelemetryCalibrationError("DifficultyAnalysis, ChallengeScoreResult, and LaneMappingResult are required")
        if analysis.challenge_score_digest != score.digest() or analysis.lane_mapping_digest != lane.digest() or lane.score_digest != score.digest():
            raise TelemetryCalibrationError("M04 analysis, Challenge Score, and lane mapping are not exactly cross-bound")
        if score.policy_version != lane.score_policy_version or lane.mapping_policy_version != "SCORE_LANE_V1":
            raise TelemetryCalibrationError("M04 policy versions are not supported")
        return cls(analysis.digest(), analysis.level_metrics_digest, score.digest(), score.policy_version, lane.digest(), lane.mapping_policy_version, score.score, lane.lane.value)

    def canonical_dict(self) -> dict[str, object]:
        return {"schema": "scrubbots-m04-difficulty-binding", "version": self.binding_version, "analysis_digest": self.analysis_digest, "level_metrics_digest": self.level_metrics_digest, "challenge_score_digest": self.challenge_score_digest, "challenge_score_policy_version": self.challenge_score_policy_version, "lane_mapping_digest": self.lane_mapping_digest, "lane_mapping_policy_version": self.lane_mapping_policy_version, "challenge_score": self.challenge_score, "lane": self.lane}


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def _median(values: list[int]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    middle = len(ordered) // 2
    value = ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2
    return round(float(value), 6)


@dataclass(frozen=True, slots=True)
class TelemetryAggregate:
    level_id: str
    candidate_id: str | None
    game_version: str
    cohort_version: str
    accepted_session_count: int
    win_rate: float
    loss_rate: float
    completion_rate: float
    median_completion_duration_ms: float | None
    retry_rate: float
    quit_abandon_rate: float
    booster_use_rate: float
    attempt_distribution: tuple[tuple[int, int], ...]
    session_digests: tuple[str, ...]
    observed_pressure: float
    predicted_pressure: float
    observed_vs_predicted_delta: float
    aggregate_digest: str = ""
    schema_version: int = TELEMETRY_AGGREGATE_VERSION

    def __post_init__(self) -> None:
        _require_token(self.level_id, "aggregate level_id")
        if self.candidate_id is not None:
            _require_token(self.candidate_id, "aggregate candidate_id")
        _require_token(self.game_version, "aggregate game_version")
        _require_token(self.cohort_version, "aggregate cohort_version")
        if type(self.schema_version) is not int or self.schema_version != TELEMETRY_AGGREGATE_VERSION:
            raise TelemetryCalibrationError("unsupported telemetry aggregate version")
        _count(self.accepted_session_count, "accepted_session_count")
        if type(self.session_digests) is not tuple or len(self.session_digests) != self.accepted_session_count or any(_SHA256.fullmatch(value or "") is None for value in self.session_digests):
            raise TelemetryCalibrationError("aggregate session digests are malformed")
        if tuple(sorted(self.session_digests)) != self.session_digests or len(set(self.session_digests)) != len(self.session_digests):
            raise TelemetryCalibrationError("aggregate session digests must be unique and ordered")
        for value, label in ((self.win_rate, "win_rate"), (self.loss_rate, "loss_rate"), (self.completion_rate, "completion_rate"), (self.retry_rate, "retry_rate"), (self.quit_abandon_rate, "quit_abandon_rate"), (self.booster_use_rate, "booster_use_rate"), (self.observed_pressure, "observed_pressure"), (self.predicted_pressure, "predicted_pressure")):
            _number(value, label, maximum=1.0)
        if self.median_completion_duration_ms is not None:
            _number(self.median_completion_duration_ms, "median_completion_duration_ms")
        if type(self.attempt_distribution) is not tuple or any(type(item) is not tuple or len(item) != 2 or type(item[0]) is not int or item[0] < 1 or type(item[1]) is not int or item[1] < 1 for item in self.attempt_distribution):
            raise TelemetryCalibrationError("attempt distribution is malformed")
        expected_delta = round(self.observed_pressure - self.predicted_pressure, 6)
        if not math.isclose(self.observed_vs_predicted_delta, expected_delta, rel_tol=0.0, abs_tol=1e-12):
            raise TelemetryCalibrationError("aggregate divergence is inconsistent")
        expected = _digest(self._identity_dict())
        if self.aggregate_digest and self.aggregate_digest != expected:
            raise TelemetryCalibrationError("aggregate digest does not match its immutable content")
        object.__setattr__(self, "aggregate_digest", expected)

    def _identity_dict(self) -> dict[str, object]:
        return {"schema": TELEMETRY_AGGREGATE_SCHEMA, "version": self.schema_version, "level_id": self.level_id, "candidate_id": self.candidate_id, "game_version": self.game_version, "cohort_version": self.cohort_version, "accepted_session_count": self.accepted_session_count, "win_rate": self.win_rate, "loss_rate": self.loss_rate, "completion_rate": self.completion_rate, "median_completion_duration_ms": self.median_completion_duration_ms, "retry_rate": self.retry_rate, "quit_abandon_rate": self.quit_abandon_rate, "booster_use_rate": self.booster_use_rate, "attempt_distribution": [[attempts, count] for attempts, count in self.attempt_distribution], "session_digests": list(self.session_digests), "observed_pressure": self.observed_pressure, "predicted_pressure": self.predicted_pressure, "observed_vs_predicted_delta": self.observed_vs_predicted_delta}

    def canonical_dict(self) -> dict[str, object]:
        return {**self._identity_dict(), "aggregate_digest": self.aggregate_digest}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return self.aggregate_digest

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "TelemetryAggregate":
        fields = set(cls("a", None, "b", "c", 0, 0.0, 0.0, 0.0, None, 0.0, 0.0, 0.0, (), (), 0.0, 0.0, 0.0).canonical_dict())
        if not isinstance(payload, Mapping) or set(payload) != fields or payload["schema"] != TELEMETRY_AGGREGATE_SCHEMA:
            raise TelemetryCalibrationError("telemetry aggregate has unknown or unsupported fields")
        return cls(payload["level_id"], payload["candidate_id"], payload["game_version"], payload["cohort_version"], payload["accepted_session_count"], payload["win_rate"], payload["loss_rate"], payload["completion_rate"], payload["median_completion_duration_ms"], payload["retry_rate"], payload["quit_abandon_rate"], payload["booster_use_rate"], tuple((item[0], item[1]) for item in payload["attempt_distribution"]), tuple(payload["session_digests"]), payload["observed_pressure"], payload["predicted_pressure"], payload["observed_vs_predicted_delta"], payload["aggregate_digest"], payload["version"])


@dataclass(frozen=True, slots=True)
class AggregateRetentionRecord:
    aggregate: TelemetryAggregate
    created_at: str | datetime
    retention_days: int = AGGREGATE_CALIBRATION_RETENTION_DAYS

    def __post_init__(self) -> None:
        if not isinstance(self.aggregate, TelemetryAggregate):
            raise TelemetryCalibrationError("aggregate retention record requires a TelemetryAggregate")
        object.__setattr__(self, "created_at", _utc_timestamp(self.created_at, "aggregate created_at"))
        if type(self.retention_days) is not int or self.retention_days < 1 or self.retention_days > AGGREGATE_CALIBRATION_RETENTION_DAYS:
            raise TelemetryCalibrationError("aggregate retention exceeds the approved 12-month maximum")

    def is_active(self, as_of: str | datetime) -> bool:
        age = _as_of(as_of) - _timestamp_value(self.created_at)
        return timedelta(0) <= age <= timedelta(days=self.retention_days)


def select_active_aggregate_records(records: Iterable[AggregateRetentionRecord], *, as_of: str | datetime) -> tuple[AggregateRetentionRecord, ...]:
    if records is None:
        return ()
    selected = [record for record in records if isinstance(record, AggregateRetentionRecord) and record.is_active(as_of)]
    return tuple(sorted(selected, key=lambda record: (record.created_at, record.aggregate.digest())))


@dataclass(frozen=True, slots=True)
class DivergenceEvidence:
    predicted_score: float
    predicted_lane: str
    predicted_pressure: float
    observed_pressure: float
    delta: float

    def __post_init__(self) -> None:
        _number(self.predicted_score, "predicted_score", maximum=100.0)
        _require_token(self.predicted_lane, "predicted_lane")
        _number(self.predicted_pressure, "predicted_pressure", maximum=1.0)
        _number(self.observed_pressure, "observed_pressure", maximum=1.0)
        if not math.isclose(self.delta, round(self.observed_pressure - self.predicted_pressure, 6), rel_tol=0.0, abs_tol=1e-12):
            raise TelemetryCalibrationError("divergence evidence is inconsistent")

    def canonical_dict(self) -> dict[str, object]:
        return {"predicted_score": self.predicted_score, "predicted_lane": self.predicted_lane, "predicted_pressure": self.predicted_pressure, "observed_pressure": self.observed_pressure, "delta": self.delta}


@dataclass(frozen=True, slots=True)
class CalibrationReport:
    m04_binding: M04DifficultyBinding
    disposition: CalibrationDisposition | str
    level_id: str | None
    candidate_id: str | None
    game_version: str | None
    cohort_version: str | None
    valid_session_count: int
    aggregate: TelemetryAggregate | None
    divergence: DivergenceEvidence | None
    advisory_review: str | None
    reason: str
    report_digest: str = ""
    schema_version: int = TELEMETRY_REPORT_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.m04_binding, M04DifficultyBinding):
            raise TelemetryCalibrationError("calibration report requires an M04 binding")
        try:
            disposition = self.disposition if isinstance(self.disposition, CalibrationDisposition) else CalibrationDisposition(self.disposition)
        except (TypeError, ValueError) as exc:
            raise TelemetryCalibrationError("calibration disposition is not approved") from exc
        object.__setattr__(self, "disposition", disposition)
        for value, label in ((self.level_id, "report level_id"), (self.game_version, "report game_version"), (self.cohort_version, "report cohort_version")):
            if value is not None:
                _require_token(value, label)
        if self.candidate_id is not None:
            _require_token(self.candidate_id, "report candidate_id")
        _count(self.valid_session_count, "valid_session_count")
        if self.aggregate is not None and not isinstance(self.aggregate, TelemetryAggregate):
            raise TelemetryCalibrationError("report aggregate is malformed")
        if self.aggregate is not None and self.valid_session_count != self.aggregate.accepted_session_count:
            raise TelemetryCalibrationError("report valid session count is not bound to aggregate")
        if self.divergence is not None and not isinstance(self.divergence, DivergenceEvidence):
            raise TelemetryCalibrationError("report divergence evidence is malformed")
        if type(self.reason) is not str or not self.reason.strip():
            raise TelemetryCalibrationError("report reason is required")
        if self.disposition is CalibrationDisposition.ADVISORY_READY and self.valid_session_count < MINIMUM_VALID_SESSIONS:
            raise TelemetryCalibrationError("ADVISORY_READY requires at least 100 valid sessions")
        if type(self.schema_version) is not int or self.schema_version != TELEMETRY_REPORT_VERSION:
            raise TelemetryCalibrationError("unsupported calibration report version")
        expected = _digest(self._identity_dict())
        if self.report_digest and self.report_digest != expected:
            raise TelemetryCalibrationError("calibration report digest does not match its immutable content")
        object.__setattr__(self, "report_digest", expected)

    def _identity_dict(self) -> dict[str, object]:
        return {"schema": TELEMETRY_REPORT_SCHEMA, "version": self.schema_version, "policy_version": TELEMETRY_POLICY_VERSION, "m04_binding": self.m04_binding.canonical_dict(), "disposition": self.disposition.value, "level_id": self.level_id, "candidate_id": self.candidate_id, "game_version": self.game_version, "cohort_version": self.cohort_version, "valid_session_count": self.valid_session_count, "aggregate": self.aggregate.canonical_dict() if self.aggregate else None, "divergence": self.divergence.canonical_dict() if self.divergence else None, "advisory_review": self.advisory_review, "reason": self.reason}

    def canonical_dict(self) -> dict[str, object]:
        return {**self._identity_dict(), "report_digest": self.report_digest}

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self.canonical_dict())

    def digest(self) -> str:
        return self.report_digest


def _binding_from_input(binding_or_analysis: M04DifficultyBinding | DifficultyAnalysis, score_result: ChallengeScoreResult | None, lane_result: LaneMappingResult | None) -> M04DifficultyBinding:
    if isinstance(binding_or_analysis, M04DifficultyBinding):
        return binding_or_analysis
    if isinstance(binding_or_analysis, DifficultyAnalysis) and isinstance(score_result, ChallengeScoreResult) and isinstance(lane_result, LaneMappingResult):
        return M04DifficultyBinding.from_results(binding_or_analysis, score_result, lane_result)
    raise TelemetryCalibrationError("an M04DifficultyBinding or all three M04 result objects are required")


def _report(binding: M04DifficultyBinding, disposition: CalibrationDisposition, *, reason: str, level_id: str | None = None, candidate_id: str | None = None, game_version: str | None = None, cohort_version: str | None = None, aggregate: TelemetryAggregate | None = None, divergence: DivergenceEvidence | None = None, advisory_review: str | None = None) -> CalibrationReport:
    return CalibrationReport(binding, disposition, level_id, candidate_id, game_version, cohort_version, aggregate.accepted_session_count if aggregate else 0, aggregate, divergence, advisory_review, reason)


def _aggregate(binding: M04DifficultyBinding, sessions: tuple[TelemetrySession, ...]) -> tuple[TelemetryAggregate, DivergenceEvidence]:
    total = len(sessions)
    wins = sum(session.terminal_kind is TelemetryEventKind.WIN for session in sessions)
    losses = sum(session.terminal_kind is TelemetryEventKind.LOSS for session in sessions)
    completed = wins + losses
    retry = sum(session.restart_count > 0 for session in sessions)
    quit_abandon = sum(session.terminal_kind in {TelemetryEventKind.QUIT, TelemetryEventKind.ABANDON} for session in sessions)
    booster = sum(session.booster_usage_count > 0 for session in sessions)
    distribution: dict[int, int] = {}
    for session in sessions:
        distribution[session.attempt_count] = distribution.get(session.attempt_count, 0) + 1
    observed_pressure = round((_ratio(losses, total) + _ratio(retry, total) + _ratio(quit_abandon, total)) / 3, 6) if total else 0.0
    predicted_pressure = round(binding.challenge_score / 100.0, 6)
    aggregate = TelemetryAggregate(sessions[0].level_id, sessions[0].candidate_id, sessions[0].game_version, sessions[0].cohort_version, total, _ratio(wins, total), _ratio(losses, total), _ratio(completed, total), _median([session.completion_duration_ms for session in sessions if session.completion_duration_ms is not None]), _ratio(retry, total), _ratio(quit_abandon, total), _ratio(booster, total), tuple(sorted(distribution.items())), tuple(sorted(session.digest() for session in sessions)), observed_pressure, predicted_pressure, round(observed_pressure - predicted_pressure, 6))
    divergence = DivergenceEvidence(binding.challenge_score, binding.lane, predicted_pressure, observed_pressure, aggregate.observed_vs_predicted_delta)
    return aggregate, divergence


def build_calibration_report(
    binding_or_analysis: M04DifficultyBinding | DifficultyAnalysis,
    sessions: Iterable[TelemetrySession | Mapping[str, object]] | None = None,
    *,
    as_of: str | datetime,
    analytics_available: bool = True,
    score_result: ChallengeScoreResult | None = None,
    lane_result: LaneMappingResult | None = None,
    level_id: str | None = None,
    candidate_id: str | None = None,
    game_version: str | None = None,
    cohort_version: str | None = None,
) -> CalibrationReport:
    """Build a deterministic advisory report without changing M04 truth."""

    binding = _binding_from_input(binding_or_analysis, score_result, lane_result)
    cutoff_end = _as_of(as_of)
    if not analytics_available or sessions is None:
        return _report(binding, CalibrationDisposition.UNAVAILABLE, reason="analytics evidence is unavailable; canonical M04 difficulty is unchanged")
    try:
        raw_sessions = tuple(sessions)
    except TypeError:
        return _report(binding, CalibrationDisposition.ERROR, reason="analytics evidence is not iterable")
    valid: list[TelemetrySession] = []
    seen: set[str] = set()
    mismatch_reason: str | None = None
    invalid_count = 0
    cutoff_start = cutoff_end - timedelta(days=RAW_TELEMETRY_RETENTION_DAYS)
    for item in raw_sessions:
        try:
            session = item if isinstance(item, TelemetrySession) else TelemetrySession.from_dict(item)
        except (TelemetryCalibrationError, TypeError, KeyError):
            invalid_count += 1
            continue
        recorded = _timestamp_value(session.recorded_at)
        if recorded < cutoff_start or recorded > cutoff_end:
            continue
        if not session.is_valid_gameplay_session():
            invalid_count += 1
            continue
        if session.session_id in seen:
            continue
        seen.add(session.session_id)
        target = (level_id, candidate_id, game_version, cohort_version)
        observed = (session.level_id, session.candidate_id, session.game_version, session.cohort_version)
        if any(expected is not None and expected != actual for expected, actual in zip(target, observed)):
            mismatch_reason = "telemetry session scope does not match the requested level, candidate, build, or cohort"
            continue
        if (session.m04_analysis_digest, session.challenge_score_digest, session.lane_mapping_digest, session.challenge_score_policy_version, session.lane_mapping_policy_version, session.challenge_score, session.lane) != (binding.analysis_digest, binding.challenge_score_digest, binding.lane_mapping_digest, binding.challenge_score_policy_version, binding.lane_mapping_policy_version, binding.challenge_score, binding.lane):
            mismatch_reason = "telemetry session is not bound to the exact accepted M04 analysis, Challenge Score, and lane"
            continue
        valid.append(session)
    if mismatch_reason is not None:
        return _report(binding, CalibrationDisposition.INCONCLUSIVE, reason=mismatch_reason, level_id=level_id, candidate_id=candidate_id, game_version=game_version, cohort_version=cohort_version)
    valid.sort(key=lambda session: (session.recorded_at, session.session_id))
    if not valid:
        return _report(binding, CalibrationDisposition.INSUFFICIENT_DATA, reason=f"no valid in-retention sessions were available ({invalid_count} invalid records excluded)", level_id=level_id, candidate_id=candidate_id, game_version=game_version, cohort_version=cohort_version)
    if level_id is None:
        level_id = valid[0].level_id
    if candidate_id is None:
        candidate_id = valid[0].candidate_id
    if game_version is None:
        game_version = valid[0].game_version
    if cohort_version is None:
        cohort_version = valid[0].cohort_version
    if any((session.level_id, session.candidate_id, session.game_version, session.cohort_version) != (level_id, candidate_id, game_version, cohort_version) for session in valid):
        return _report(binding, CalibrationDisposition.INCONCLUSIVE, reason="valid evidence spans more than one exact calibration scope", level_id=level_id, candidate_id=candidate_id, game_version=game_version, cohort_version=cohort_version)
    aggregate, divergence = _aggregate(binding, tuple(valid))
    disposition = CalibrationDisposition.ADVISORY_READY if aggregate.accepted_session_count >= MINIMUM_VALID_SESSIONS else CalibrationDisposition.INSUFFICIENT_DATA
    review = "REVIEW_ADVISORY_DIVERGENCE" if disposition is CalibrationDisposition.ADVISORY_READY and divergence.delta != 0.0 else None
    reason = "deterministic advisory aggregate meets the 100-session threshold; M04 remains canonical" if disposition is CalibrationDisposition.ADVISORY_READY else f"{aggregate.accepted_session_count} valid sessions are below the 100-session recommendation threshold"
    return _report(binding, disposition, reason=reason, level_id=level_id, candidate_id=candidate_id, game_version=game_version, cohort_version=cohort_version, aggregate=aggregate, divergence=divergence, advisory_review=review)


def calibrate_telemetry(*args: object, **kwargs: object) -> CalibrationReport:
    """Stable short alias for the report builder."""

    return build_calibration_report(*args, **kwargs)  # type: ignore[arg-type]


def validate_telemetry_payload(payload: Mapping[str, object]) -> TelemetrySession:
    """Strictly parse an approved session and reject unknown/PII fields."""

    return TelemetrySession.from_dict(payload)


__all__ = [
    "AGGREGATE_CALIBRATION_RETENTION_DAYS",
    "AggregateRetentionRecord",
    "CalibrationDisposition",
    "CalibrationReport",
    "DivergenceEvidence",
    "M04DifficultyBinding",
    "MINIMUM_VALID_SESSIONS",
    "RAW_TELEMETRY_RETENTION_DAYS",
    "TELEMETRY_AGGREGATE_SCHEMA",
    "TELEMETRY_AGGREGATE_VERSION",
    "TELEMETRY_EVENT_SCHEMA",
    "TELEMETRY_EVENT_VERSION",
    "TELEMETRY_POLICY_VERSION",
    "TELEMETRY_REPORT_SCHEMA",
    "TELEMETRY_REPORT_VERSION",
    "TELEMETRY_SCHEMA_VERSION",
    "TELEMETRY_SESSION_SCHEMA",
    "TELEMETRY_SESSION_VERSION",
    "TelemetryAggregate",
    "TelemetryCalibrationError",
    "TelemetryEvent",
    "TelemetryEventKind",
    "TelemetrySession",
    "build_calibration_report",
    "calibrate_telemetry",
    "select_active_aggregate_records",
    "validate_telemetry_payload",
]
