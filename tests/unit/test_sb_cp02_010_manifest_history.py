from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "content_pipeline" / "src"))

from scrubbots_content_pipeline import (
    ManifestHistoryError,
    ManifestHistoryReasonCode,
    ManifestHistoryV1,
    append_manifest_history,
    historical_manifest_json,
    parse_manifest_history,
    serialize_manifest_history,
    verify_manifest_history,
)


def _manifest(version: int, *, schema: str = "scrubbots.content.manifest.v1") -> bytes:
    return json.dumps(
        {"schema": schema, "schema_version": 1, "content_version": version, "opaque": {"v": version}},
        sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")


def _history():
    empty = ManifestHistoryV1()
    first = append_manifest_history(empty, _manifest(1), recorded_at_utc="2026-10-06T09:00:00Z")
    second = append_manifest_history(first, _manifest(4), recorded_at_utc="2026-10-06T09:01:00Z")
    return second


def test_history_is_append_only_monotonic_hash_chained_and_deterministic() -> None:
    history = _history()
    result = verify_manifest_history(history)
    assert result.accepted is True
    assert result.reason_code is ManifestHistoryReasonCode.VALID
    assert [record.sequence for record in history.records] == [1, 2]
    assert [record.content_version for record in history.records] == [1, 4]
    assert history.records[1].previous_record_sha256 == history.records[0].record_sha256

    encoded = serialize_manifest_history(history)
    assert encoded == serialize_manifest_history(parse_manifest_history(encoded))
    assert parse_manifest_history(encoded) == history
    assert verify_manifest_history(history, expected_tip_sha256=result.tip_sha256).accepted is True
    assert verify_manifest_history(history, expected_tip_sha256="0" * 64).reason_code is ManifestHistoryReasonCode.EXPECTED_TIP_MISMATCH


def test_history_rejects_duplicate_or_decreasing_content_versions_and_non_utc_time() -> None:
    first = append_manifest_history(ManifestHistoryV1(), _manifest(3), recorded_at_utc="2026-10-06T09:00:00Z")
    for version in (3, 2):
        with pytest.raises(ManifestHistoryError) as exc:
            append_manifest_history(first, _manifest(version), recorded_at_utc="2026-10-06T09:01:00Z")
        assert exc.value.reason_code is ManifestHistoryReasonCode.CONTENT_VERSION_NOT_INCREASED

    with pytest.raises(ManifestHistoryError) as exc:
        append_manifest_history(first, _manifest(4), recorded_at_utc="2026-10-06T11:01:00+02:00")
    assert exc.value.reason_code is ManifestHistoryReasonCode.INVALID_RECORD_TIME


def test_history_detects_reorder_deletion_link_byte_and_digest_mutation() -> None:
    history = _history()
    first, second = history.records

    reordered = ManifestHistoryV1((second, first))
    assert verify_manifest_history(reordered).reason_code is ManifestHistoryReasonCode.SEQUENCE_MISMATCH
    deleted = ManifestHistoryV1((second,))
    assert verify_manifest_history(deleted).reason_code is ManifestHistoryReasonCode.SEQUENCE_MISMATCH

    changed_bytes = replace(first, manifest_bytes=first.manifest_bytes + b" ")
    assert verify_manifest_history(ManifestHistoryV1((changed_bytes, second))).reason_code is ManifestHistoryReasonCode.MANIFEST_SHA256_MISMATCH

    changed_link = replace(second, previous_record_sha256="0" * 64)
    assert verify_manifest_history(ManifestHistoryV1((first, changed_link))).reason_code is ManifestHistoryReasonCode.PREVIOUS_RECORD_MISMATCH

    changed_digest = replace(second, record_sha256="0" * 64)
    assert verify_manifest_history(ManifestHistoryV1((first, changed_digest))).reason_code is ManifestHistoryReasonCode.RECORD_SHA256_MISMATCH

    truncated = ManifestHistoryV1((first,))
    pinned_truncation = ManifestHistoryV1((first,), history.tip_sha256)
    assert verify_manifest_history(pinned_truncation).reason_code is ManifestHistoryReasonCode.EXPECTED_TIP_MISMATCH
    assert verify_manifest_history(truncated, expected_tip_sha256=second.record_sha256).reason_code is ManifestHistoryReasonCode.EXPECTED_TIP_MISMATCH


def test_history_keeps_old_schema_bytes_inspectable_without_current_schema_acceptance() -> None:
    old_bytes = _manifest(7, schema="scrubbots.content.manifest.v0")
    history = append_manifest_history(ManifestHistoryV1(), old_bytes, recorded_at_utc="2026-10-06T09:02:00Z")
    record = parse_manifest_history(serialize_manifest_history(history)).records[0]
    assert record.manifest_bytes == old_bytes
    assert historical_manifest_json(record)["schema"] == "scrubbots.content.manifest.v0"


def test_history_rejects_malformed_manifest_or_mutated_serialization() -> None:
    with pytest.raises(ManifestHistoryError) as exc:
        append_manifest_history(ManifestHistoryV1(), b"not json", recorded_at_utc="2026-10-06T09:03:00Z")
    assert exc.value.reason_code is ManifestHistoryReasonCode.INVALID_MANIFEST_BYTES

    encoded = serialize_manifest_history(_history())
    tampered = encoded.replace(b"content_version", b"content_versioN", 1)
    with pytest.raises(ManifestHistoryError):
        parse_manifest_history(tampered)
