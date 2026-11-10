"""Offline, truthful Content Platform operational evidence helpers.

These pure functions consume already-observed bytes and records. They never
contact a provider, write remote content, or infer a successful observation.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, timezone
import base64
import hashlib
import json
import re
from pathlib import Path


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_EVENT_KINDS = frozenset({
    "BATCH", "STAGING_VERSION", "PRODUCTION_VERSION", "OBJECT_VERIFY",
    "DISABLE", "SCHEDULE", "SCHEDULE_CANCEL", "ROLLBACK", "ERROR",
})
_OUTCOMES = frozenset({"PREPARED", "COMPLETED", "BLOCKED", "FAILED", "MATCH", "MISMATCH"})
_ENVIRONMENTS = frozenset({"LOCAL", "STAGING", "PRODUCTION"})
MAX_BACKUP_BYTES = 16 * 1024 * 1024
MAX_BACKUP_OBJECTS = 128
OPERATION_RECORD_SCHEMA_VERSION = 2


class OperationsEvidenceError(ValueError):
    """Raised when operational evidence is incomplete or unsafe to serialize."""


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def _identifier(value: object, label: str) -> str:
    if type(value) is not str or not _IDENTIFIER.fullmatch(value):
        raise OperationsEvidenceError(f"{label} must be a bounded opaque identifier")
    if re.search(r"(?i)(secret|token|password|api[-_]?key|access[-_]?key)", value):
        raise OperationsEvidenceError(f"{label} must not contain secret-like text")
    return value


def _digest(value: object, label: str) -> str:
    if type(value) is not str or not _SHA256.fullmatch(value):
        raise OperationsEvidenceError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _object_key(value: object, label: str) -> str:
    if type(value) is not str or len(value) > 512 or "\\" in value or value.startswith("/"):
        raise OperationsEvidenceError(f"{label} must be a bounded relative slash path")
    parts = value.split("/")
    if any(part in {"", ".", ".."} or not _IDENTIFIER.fullmatch(part) for part in parts):
        raise OperationsEvidenceError(f"{label} contains an unsafe path component")
    return value


@dataclass(frozen=True, slots=True)
class OperationRecord:
    """Small secret-free event record; intentionally has no free-form message."""

    operation_id: str
    occurred_at: str
    kind: str
    environment: str
    outcome: str
    reason_code: str
    batch_id: str | None = None
    target_id: str | None = None
    content_version: int | None = None
    manifest_sha256: str | None = None
    expected_object_sha256: str | None = None
    observed_object_sha256: str | None = None

    def __post_init__(self) -> None:
        _identifier(self.operation_id, "operation_id")
        _identifier(self.reason_code, "reason_code")
        if type(self.kind) is not str or self.kind not in _EVENT_KINDS:
            raise OperationsEvidenceError("kind must be a supported operational event")
        if type(self.environment) is not str or self.environment not in _ENVIRONMENTS:
            raise OperationsEvidenceError("environment must be LOCAL, STAGING, or PRODUCTION")
        if type(self.outcome) is not str or self.outcome not in _OUTCOMES:
            raise OperationsEvidenceError("outcome must be an observed, non-inferred disposition")
        try:
            timestamp = datetime.fromisoformat(self.occurred_at.replace("Z", "+00:00"))
        except (AttributeError, TypeError, ValueError) as exc:
            raise OperationsEvidenceError("occurred_at must be an offset-aware ISO-8601 timestamp") from exc
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise OperationsEvidenceError("occurred_at must include a timezone")
        if self.batch_id is not None:
            _identifier(self.batch_id, "batch_id")
        if self.target_id is not None:
            _identifier(self.target_id, "target_id")
        if self.content_version is not None and (type(self.content_version) is not int or self.content_version < 1):
            raise OperationsEvidenceError("content_version must be a positive integer when provided")
        if self.manifest_sha256 is not None:
            _digest(self.manifest_sha256, "manifest_sha256")
        if self.expected_object_sha256 is not None:
            _digest(self.expected_object_sha256, "expected_object_sha256")
        if self.observed_object_sha256 is not None:
            _digest(self.observed_object_sha256, "observed_object_sha256")
        version_event_environment = {
            "STAGING_VERSION": "STAGING",
            "PRODUCTION_VERSION": "PRODUCTION",
        }.get(self.kind)
        if version_event_environment is not None:
            if self.environment != version_event_environment:
                raise OperationsEvidenceError("version event kind must match its environment")
            if self.content_version is None or self.manifest_sha256 is None:
                raise OperationsEvidenceError("version events require an observed manifest version and digest")
        if self.kind == "OBJECT_VERIFY":
            if self.expected_object_sha256 is None or self.observed_object_sha256 is None:
                raise OperationsEvidenceError("OBJECT_VERIFY requires expected and observed object digests")
            if self.outcome not in {"MATCH", "MISMATCH"}:
                raise OperationsEvidenceError("OBJECT_VERIFY outcome must compare observed digests")
            if self.outcome == "MATCH" and self.expected_object_sha256 != self.observed_object_sha256:
                raise OperationsEvidenceError("MATCH requires identical expected and observed object digests")
            if self.outcome == "MISMATCH" and self.expected_object_sha256 == self.observed_object_sha256:
                raise OperationsEvidenceError("MISMATCH requires different expected and observed object digests")

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "scrubbots-content-operation-record",
            "schema_version": OPERATION_RECORD_SCHEMA_VERSION,
            "operation_id": self.operation_id,
            "occurred_at": self.occurred_at,
            "kind": self.kind,
            "environment": self.environment,
            "outcome": self.outcome,
            "reason_code": self.reason_code,
            "batch_id": self.batch_id,
            "target_id": self.target_id,
            "content_version": self.content_version,
            "manifest_sha256": self.manifest_sha256,
            "expected_object_sha256": self.expected_object_sha256,
            "observed_object_sha256": self.observed_object_sha256,
        }

    def canonical_bytes(self) -> bytes:
        return _canonical(self.as_dict())

    @property
    def record_sha256(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def operation_record_from_publication_plan(
    plan: object,
    *,
    operation_id: str,
    occurred_at: str,
) -> OperationRecord:
    """Adapt a CP03 publication plan into fixed-field local operation evidence.

    This pure in-memory bridge never treats a plan as a completed publication
    and refuses plans that claim a remote mutation. It records only the opaque
    content ID, disposition, and a bounded reason code; payloads, target IDs,
    credentials, and free-form messages are excluded.
    """
    from .publication_plan import (
        PUBLICATION_PLAN_VERSION,
        PlanCheck,
        PublicationPlan,
        _has_publication_plan_builder_provenance,
        _publication_check_reason,
        _required_publication_check_ids,
    )

    if type(plan) is not PublicationPlan or not _has_publication_plan_builder_provenance(plan):
        raise OperationsEvidenceError("publication plan lacks intact canonical builder provenance")
    if plan.plan_version != PUBLICATION_PLAN_VERSION or plan.remote_mutation_performed is not False:
        raise OperationsEvidenceError("publication plan version or mutation disposition is invalid")
    if plan.target_environment not in {"staging", "production"}:
        raise OperationsEvidenceError("publication plan environment must be staging or production")
    if (type(plan.accepted) is not bool or type(plan.complete) is not bool
            or plan.complete is not True or type(plan.owner_approved) is not bool
            or type(plan.mutation_eligible_in_principle) is not bool):
        raise OperationsEvidenceError("publication plan disposition is invalid")
    required_check_ids = _required_publication_check_ids(plan.target_environment)
    if required_check_ids is None:
        raise OperationsEvidenceError("publication plan environment has no canonical check contract")
    if not isinstance(plan.checks, tuple) or any(
        type(check) is not PlanCheck
        or type(check.check_id) is not str
        or type(check.accepted) is not bool
        or type(check.reason_code) is not str
        for check in plan.checks
    ):
        raise OperationsEvidenceError("publication plan checks are malformed")
    check_ids = tuple(check.check_id for check in plan.checks)
    if check_ids != required_check_ids or len(set(check_ids)) != len(required_check_ids):
        raise OperationsEvidenceError("publication plan required checks are incomplete, duplicated, or out of contract")
    if any(check.reason_code != _publication_check_reason(check.check_id, check.accepted)
           for check in plan.checks):
        raise OperationsEvidenceError("publication plan check reason does not match its disposition")
    if plan.accepted is not all(check.accepted for check in plan.checks):
        raise OperationsEvidenceError("publication plan accepted flag contradicts its checks")
    approval_check = next(check for check in plan.checks if check.check_id == "owner_approval")
    if approval_check.accepted is not plan.owner_approved:
        raise OperationsEvidenceError("publication plan owner approval contradicts its check")
    if plan.mutation_eligible_in_principle is not (plan.accepted and plan.owner_approved):
        raise OperationsEvidenceError("publication plan mutation eligibility contradicts its checks")
    if (not isinstance(plan.content_id, str) or not _IDENTIFIER.fullmatch(plan.content_id)
            or not isinstance(plan.content_digest, str) or not _SHA256.fullmatch(plan.content_digest)
            or not isinstance(plan.target_id, str) or not _IDENTIFIER.fullmatch(plan.target_id)):
        raise OperationsEvidenceError("publication plan content or target identity is invalid")
    expected_operation = "promote_staged_record" if plan.target_environment == "production" else "publish_to_staging"
    if (not isinstance(plan.operations, tuple) or len(plan.operations) != 1
            or plan.operations[0].sequence != 1
            or plan.operations[0].operation != expected_operation
            or plan.operations[0].content_id != plan.content_id
            or plan.operations[0].content_digest != plan.content_digest):
        raise OperationsEvidenceError("publication plan operation does not match its environment and content")
    failed = next((check for check in plan.checks if check.accepted is False), None)
    ready = plan.accepted is True and plan.complete is True and failed is None
    reason_code = "PREFLIGHT_READY" if ready else (failed.reason_code if failed else "PREFLIGHT_BLOCKED")
    return OperationRecord(
        operation_id=operation_id,
        occurred_at=occurred_at,
        kind="BATCH",
        environment=plan.target_environment.upper(),
        outcome="PREPARED" if ready else "BLOCKED",
        reason_code=reason_code,
        batch_id=plan.content_id,
    )


def operation_record_from_manifest_observation(
    observed_manifest_bytes: bytes | None,
    *,
    environment: str,
    operation_id: str,
    occurred_at: str,
) -> OperationRecord:
    """Record a staging/production version only from strict-parsed observed bytes.

    This pure helper has no provider access. Missing observations fail closed;
    the returned version and digest are derived from the exact same bytes.
    """
    if type(environment) is not str or environment not in {"STAGING", "PRODUCTION"}:
        raise OperationsEvidenceError("version observations require STAGING or PRODUCTION environment")
    if type(observed_manifest_bytes) is not bytes:
        raise OperationsEvidenceError("manifest bytes must be explicitly observed before recording a version")
    from .manifest_parser import ManifestParseError, parse_content_manifest_v1

    try:
        manifest = parse_content_manifest_v1(observed_manifest_bytes)
    except ManifestParseError as exc:
        raise OperationsEvidenceError("observed manifest is invalid") from exc
    return OperationRecord(
        operation_id=operation_id,
        occurred_at=occurred_at,
        kind="STAGING_VERSION" if environment == "STAGING" else "PRODUCTION_VERSION",
        environment=environment,
        outcome="COMPLETED",
        reason_code="VERSION_OBSERVED",
        content_version=manifest.content_version,
        manifest_sha256=hashlib.sha256(observed_manifest_bytes).hexdigest(),
    )


def operation_record_from_object_observation(
    expected_object_sha256: str,
    observed_object_bytes: bytes | None,
    *,
    environment: str,
    operation_id: str,
    occurred_at: str,
) -> OperationRecord:
    """Record an object digest comparison only when exact observed bytes exist.

    No provider is contacted; absent bytes cannot be labeled a mismatch or a
    remote verification and instead remain an unrecorded/unknown observation.
    """
    expected = _digest(expected_object_sha256, "expected_object_sha256")
    if type(environment) is not str or environment not in _ENVIRONMENTS:
        raise OperationsEvidenceError("object observation environment is invalid")
    if type(observed_object_bytes) is not bytes:
        raise OperationsEvidenceError("object bytes must be explicitly observed before recording verification")
    observed = hashlib.sha256(observed_object_bytes).hexdigest()
    matches = observed == expected
    return OperationRecord(
        operation_id=operation_id,
        occurred_at=occurred_at,
        kind="OBJECT_VERIFY",
        environment=environment,
        outcome="MATCH" if matches else "MISMATCH",
        reason_code="HASH_MATCH" if matches else "HASH_MISMATCH",
        expected_object_sha256=expected,
        observed_object_sha256=observed,
    )


def operation_record_from_control_receipt(receipt: object, *, operation_id: str) -> OperationRecord:
    """Record a validated local control intent without claiming remote activation."""
    from .m17_release_controls import ControlReceipt, ReceiptOperation, make_control_receipt, serialize_control_receipt

    if not isinstance(receipt, ControlReceipt):
        raise OperationsEvidenceError("control receipt must be a canonical M17 ControlReceipt")
    try:
        operation = ReceiptOperation(receipt.operation)
        verified = make_control_receipt(
            actor_ref=receipt.actor_ref,
            operation=operation,
            occurred_at_utc=receipt.occurred_at_utc,
            target_id=receipt.target_id,
            current_version=receipt.current_version,
            next_version=receipt.next_version,
            prior_manifest_sha256=receipt.prior_manifest_sha256,
            new_manifest_sha256=receipt.new_manifest_sha256,
            pack_hashes=receipt.pack_hashes,
            approval_id=receipt.approval_id,
            provider_record_sha256=receipt.provider_record_sha256,
            outcome=receipt.outcome,
        )
        if serialize_control_receipt(verified) != serialize_control_receipt(receipt):
            raise OperationsEvidenceError("control receipt does not match its canonical evidence")
    except OperationsEvidenceError:
        raise
    except Exception as exc:
        raise OperationsEvidenceError("control receipt is invalid") from exc

    operation_kinds = {
        "ROLLBACK": "ROLLBACK",
        "DISABLE": "DISABLE",
        "REENABLE": "DISABLE",
        "SCHEDULE": "SCHEDULE",
        "CANCEL_SCHEDULE": "SCHEDULE_CANCEL",
    }
    kind = operation_kinds.get(operation.value)
    if kind is None:
        raise OperationsEvidenceError("control operation is not an auditable CP08 change")
    expected_outcome = {
        ("SCHEDULE", "INTENT_PERSISTED"): ("PREPARED", "SCHEDULE_INTENT_PREPARED"),
        ("CANCEL_SCHEDULE", "INTENT_CANCELLED"): ("COMPLETED", "SCHEDULE_CANCEL_COMPLETED"),
        ("ROLLBACK", "PREPARED"): ("PREPARED", "ROLLBACK_PREPARED"),
        ("DISABLE", "PREPARED"): ("PREPARED", "DISABLE_PREPARED"),
        ("REENABLE", "PREPARED"): ("PREPARED", "REENABLE_PREPARED"),
    }.get((operation.value, receipt.outcome))
    if expected_outcome is None:
        raise OperationsEvidenceError("control receipt outcome is outside the local intent contract")
    disposition, reason_code = expected_outcome
    return OperationRecord(
        operation_id=operation_id,
        occurred_at=receipt.occurred_at_utc,
        kind=kind,
        environment="LOCAL",
        outcome=disposition,
        reason_code=reason_code,
        target_id=receipt.target_id,
        content_version=receipt.next_version,
        manifest_sha256=receipt.new_manifest_sha256,
    )


def render_jsonl(records: Iterable[OperationRecord]) -> bytes:
    """Serialize only validated fields, with no email or credential payload field."""
    checked = tuple(records)
    if any(not isinstance(item, OperationRecord) for item in checked):
        raise OperationsEvidenceError("all JSONL entries must be validated OperationRecord values")
    return b"".join(item.canonical_bytes() + b"\n" for item in checked)


def write_local_operation_evidence(
    output_dir: Path,
    records: Iterable[OperationRecord],
    *,
    week_start: date,
    week_end: date,
) -> tuple[Path, Path]:
    """Write one new, bounded local evidence directory without replacing owner data.

    If a write fails, rollback is confined to files and the directory created by
    this call. A pre-existing path is never opened or removed.
    """
    if not isinstance(output_dir, Path):
        raise OperationsEvidenceError("operation evidence destination must be a Path")
    resolved_parts = {part.casefold() for part in output_dir.resolve(strict=False).parts}
    if resolved_parts & {".hiveai", ".git", "tasks.md", "agents.md", "governance.md", "handoff.md"}:
        raise OperationsEvidenceError("operation evidence destination overlaps protected repository control files")
    if not output_dir.parent.is_dir() or output_dir.exists() or output_dir.is_symlink():
        raise OperationsEvidenceError("operation evidence destination must be a new directory")
    checked = tuple(records)
    jsonl = render_jsonl(checked)
    summary = weekly_batch_summary(checked, week_start, week_end)
    summary_bytes = _canonical(summary) + b"\n"
    if len(jsonl) > 1024 * 1024 or len(summary_bytes) > 1024 * 1024:
        raise OperationsEvidenceError("local operation evidence exceeds the 1 MiB per-file bound")
    created: list[Path] = []
    made_directory = False
    try:
        output_dir.mkdir(parents=True, exist_ok=False)
        made_directory = True
        for name, payload in (("operations.jsonl", jsonl), ("weekly-summary.json", summary_bytes)):
            target = output_dir / name
            with target.open("xb") as stream:
                created.append(target)
                stream.write(payload)
                stream.flush()
        return output_dir / "operations.jsonl", output_dir / "weekly-summary.json"
    except Exception as exc:
        for target in reversed(created):
            try:
                target.unlink()
            except OSError:
                pass
        if made_directory:
            try:
                output_dir.rmdir()
            except OSError:
                pass
        if isinstance(exc, OperationsEvidenceError):
            raise
        raise OperationsEvidenceError("local operation evidence write failed and created output was rolled back") from exc


def weekly_batch_summary(records: Iterable[OperationRecord], week_start: date, week_end: date) -> dict[str, object]:
    """Summarize supplied evidence only; caller supplies a half-open UTC date range."""
    if not isinstance(week_start, date) or not isinstance(week_end, date) or week_start >= week_end:
        raise OperationsEvidenceError("week range must be a non-empty half-open date interval")
    checked = tuple(records)
    if any(not isinstance(item, OperationRecord) for item in checked):
        raise OperationsEvidenceError("weekly summaries require validated OperationRecord values")
    selected = tuple(item for item in checked if week_start <= datetime.fromisoformat(
        item.occurred_at.replace("Z", "+00:00")).astimezone(timezone.utc).date() < week_end)
    selected = tuple(sorted(selected, key=lambda item: (datetime.fromisoformat(
        item.occurred_at.replace("Z", "+00:00")).astimezone(timezone.utc), item.operation_id)))
    counts = Counter((item.kind, item.outcome) for item in selected)
    payload: dict[str, object] = {
        "schema": "scrubbots-content-weekly-operations-summary",
        "schema_version": 1,
        "week_start_utc": week_start.isoformat(),
        "week_end_utc_exclusive": week_end.isoformat(),
        "record_count": len(selected),
        "records": [item.as_dict() for item in selected],
        "counts": [{"kind": kind, "outcome": outcome, "count": count}
                   for (kind, outcome), count in sorted(counts.items())],
        "recorded_object_verifications_marked_match": sum(item.kind == "OBJECT_VERIFY" and item.outcome == "MATCH" for item in selected),
    }
    payload["summary_sha256"] = hashlib.sha256(_canonical(payload)).hexdigest()
    return payload


def verify_content_health(
    manifest_bytes: bytes | None,
    *,
    expected_manifest_sha256: str,
    expected_objects: Mapping[str, str],
    observed_objects: Mapping[str, bytes] | None,
) -> dict[str, object]:
    """Verify hashes of explicitly read bytes; no reader means UNKNOWN, never healthy."""
    expected_manifest = _digest(expected_manifest_sha256, "expected_manifest_sha256")
    if not isinstance(expected_objects, Mapping) or not expected_objects:
        raise OperationsEvidenceError("expected_objects must contain at least one canonical object")
    checked_expected: dict[str, str] = {}
    for key, digest in expected_objects.items():
        _object_key(key, "object key")
        checked_expected[key] = _digest(digest, f"expected_objects[{key}]")
    # Validate caller-observed keys at the trust boundary before any manifest
    # outcome, so malformed or traversal keys always fail closed.
    if observed_objects is not None:
        if not isinstance(observed_objects, Mapping):
            raise OperationsEvidenceError("observed_objects must be an explicit key-to-bytes mapping or None")
        for key in observed_objects:
            _object_key(key, "observed object key")
    if manifest_bytes is None:
        return {"status": "UNKNOWN", "reason": "MANIFEST_BYTES_NOT_OBSERVED", "objects": []}
    if not isinstance(manifest_bytes, bytes):
        raise OperationsEvidenceError("manifest_bytes must be observed bytes or None")
    actual_manifest = hashlib.sha256(manifest_bytes).hexdigest()
    if actual_manifest != expected_manifest:
        return {"status": "FAIL", "reason": "MANIFEST_HASH_MISMATCH", "observed_manifest_sha256": actual_manifest, "objects": []}
    from .manifest_parser import ManifestParseError, parse_content_manifest_v1

    try:
        manifest = parse_content_manifest_v1(manifest_bytes)
    except ManifestParseError:
        return {"status": "FAIL", "reason": "INVALID_MANIFEST", "observed_manifest_sha256": actual_manifest,
                "objects": []}
    declared_objects = {pack.object_key: pack.sha256 for pack in manifest.packs}
    if declared_objects != checked_expected:
        return {"status": "FAIL", "reason": "MANIFEST_OBJECT_SET_MISMATCH",
                "observed_manifest_sha256": actual_manifest, "objects": []}
    if observed_objects is None:
        return {"status": "UNKNOWN", "reason": "OBJECT_BYTES_NOT_OBSERVED", "observed_manifest_sha256": actual_manifest, "objects": []}
    if not isinstance(observed_objects, Mapping):
        raise OperationsEvidenceError("observed_objects must be an explicit key-to-bytes mapping or None")
    for key in observed_objects:
        _object_key(key, "observed object key")
    results: list[dict[str, object]] = []
    for key, expected in sorted(checked_expected.items()):
        observed = observed_objects.get(key)
        digest = hashlib.sha256(observed).hexdigest() if isinstance(observed, bytes) else None
        disposition = "MISSING" if observed is None else ("MATCH" if digest == expected else "HASH_MISMATCH")
        results.append({"key": key, "expected_sha256": expected, "observed_sha256": digest, "disposition": disposition})
    unexpected = sorted(set(observed_objects) - set(checked_expected))
    status = "HEALTHY" if results and not unexpected and all(row["disposition"] == "MATCH" for row in results) else "FAIL"
    return {"status": status, "reason": "ALL_EXPECTED_BYTES_OBSERVED" if status == "HEALTHY" else "OBJECT_SET_INCOMPLETE_OR_MISMATCHED",
            "observed_manifest_sha256": actual_manifest, "objects": results, "unexpected_object_keys": unexpected}


def export_recovery_bundle(objects: Mapping[str, bytes]) -> bytes:
    """Build a bounded, deterministic in-memory backup export for tested recovery."""
    if not isinstance(objects, Mapping) or not objects or len(objects) > MAX_BACKUP_OBJECTS:
        raise OperationsEvidenceError(f"backup export requires 1..{MAX_BACKUP_OBJECTS} objects")
    entries = []
    total = 0
    for key, raw in sorted(objects.items()):
        _object_key(key, "backup object key")
        if not isinstance(raw, bytes) or not raw:
            raise OperationsEvidenceError("backup objects require safe relative keys and non-empty observed bytes")
        total += len(raw)
        if total > MAX_BACKUP_BYTES:
            raise OperationsEvidenceError("backup export exceeds the 16 MiB evidence bound")
        entries.append({"key": key, "sha256": hashlib.sha256(raw).hexdigest(), "bytes_b64": base64.b64encode(raw).decode("ascii")})
    body: dict[str, object] = {"schema": "scrubbots-content-recovery-export", "schema_version": 1, "objects": entries}
    body["bundle_sha256"] = hashlib.sha256(_canonical(body)).hexdigest()
    return _canonical(body) + b"\n"


def restore_recovery_bundle(bundle_bytes: bytes) -> dict[str, bytes]:
    """Validate a backup fully in memory before returning restored content bytes."""
    if not isinstance(bundle_bytes, bytes) or len(bundle_bytes) > MAX_BACKUP_BYTES * 2:
        raise OperationsEvidenceError("recovery export is missing or exceeds the bounded size")
    try:
        document = json.loads(bundle_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OperationsEvidenceError("recovery export is not valid UTF-8 JSON") from exc
    if (
        not isinstance(document, dict)
        or set(document) != {"schema", "schema_version", "objects", "bundle_sha256"}
        or document.get("schema") != "scrubbots-content-recovery-export"
        or type(document.get("schema_version")) is not int
        or document.get("schema_version") != 1
        or not isinstance(document.get("objects"), list)
    ):
        raise OperationsEvidenceError("recovery export does not match the supported exact schema")
    expected_bundle = _digest(document["bundle_sha256"], "bundle_sha256")
    body = {key: value for key, value in document.items() if key != "bundle_sha256"}
    if hashlib.sha256(_canonical(body)).hexdigest() != expected_bundle:
        raise OperationsEvidenceError("recovery export bundle hash does not match")
    if not 1 <= len(document["objects"]) <= MAX_BACKUP_OBJECTS:
        raise OperationsEvidenceError("recovery export object count is outside the bound")
    restored: dict[str, bytes] = {}
    total = 0
    for entry in document["objects"]:
        if not isinstance(entry, dict) or set(entry) != {"key", "sha256", "bytes_b64"}:
            raise OperationsEvidenceError("recovery export object entry has unsupported fields")
        key = entry["key"]
        _object_key(key, "backup object key")
        if key in restored:
            raise OperationsEvidenceError("recovery export object key is unsafe or duplicated")
        expected = _digest(entry["sha256"], "backup object sha256")
        if type(entry["bytes_b64"]) is not str:
            raise OperationsEvidenceError("recovery export object bytes must be base64 text")
        try:
            raw = base64.b64decode(entry["bytes_b64"], validate=True)
        except (ValueError, TypeError) as exc:
            raise OperationsEvidenceError("recovery export object bytes are not valid base64") from exc
        if not raw or hashlib.sha256(raw).hexdigest() != expected:
            raise OperationsEvidenceError("recovery export object bytes failed integrity verification")
        total += len(raw)
        if total > MAX_BACKUP_BYTES:
            raise OperationsEvidenceError("recovery export exceeds the 16 MiB evidence bound")
        restored[key] = raw
    return restored
