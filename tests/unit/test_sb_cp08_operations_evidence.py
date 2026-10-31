from __future__ import annotations

from datetime import date
import hashlib
import json
from pathlib import Path

import pytest

from scrubbots_content_pipeline import cli
from scrubbots_content_pipeline.operations import (
    OperationRecord,
    OperationsEvidenceError,
    export_recovery_bundle,
    render_jsonl,
    restore_recovery_bundle,
    verify_content_health,
    weekly_batch_summary,
)


def _record(**changes: object) -> OperationRecord:
    values: dict[str, object] = {
        "operation_id": "op-001",
        "occurred_at": "2026-10-14T08:15:00Z",
        "kind": "OBJECT_VERIFY",
        "environment": "STAGING",
        "outcome": "MATCH",
        "reason_code": "HASH_MATCH",
        "batch_id": "batch-01",
        "content_version": 4,
        "manifest_sha256": "a" * 64,
        "expected_object_sha256": "b" * 64,
        "observed_object_sha256": "b" * 64,
    }
    values.update(changes)
    return OperationRecord(**values)  # type: ignore[arg-type]


def test_weekly_summary_is_deterministic_and_records_only_observed_status() -> None:
    records = (_record(), _record(operation_id="op-002", kind="SCHEDULE_CANCEL", outcome="COMPLETED"),
               _record(operation_id="op-old", occurred_at="2026-10-07T23:59:59Z"))
    summary = weekly_batch_summary(records, date(2026, 10, 13), date(2026, 10, 20))
    assert summary == weekly_batch_summary(reversed(records), date(2026, 10, 13), date(2026, 10, 20))
    assert summary["record_count"] == 2
    assert summary["recorded_object_verifications_marked_match"] == 1
    assert [row["operation_id"] for row in summary["records"]] == ["op-001", "op-002"]  # type: ignore[index]
    assert "access_key" not in render_jsonl(records).decode("utf-8").lower()


def test_dry_run_cli_wires_blocked_preflight_into_weekly_summary_without_writing(monkeypatch, capsys) -> None:
    captured: dict[str, object] = {}

    def capture_evidence(output_dir, records, *, week_start, week_end):
        captured["summary"] = weekly_batch_summary(records, week_start, week_end)
        captured["output_dir"] = output_dir
        return output_dir / "operations.jsonl", output_dir / "weekly-summary.json"

    monkeypatch.setattr(cli, "write_local_operation_evidence", capture_evidence)
    monkeypatch.setattr(
        "sys.argv",
        ["scrubbots-content-pipeline", "--dry-run", "--environment", "staging",
         "--operations-dir", "unused-output/weekly"],
    )

    assert cli.main() == 1
    report = json.loads(capsys.readouterr().out)
    summary = captured["summary"]
    assert report["remote_mutation_performed"] is False
    assert summary["record_count"] == 1  # type: ignore[index]
    assert summary["records"][0]["kind"] == "ERROR"  # type: ignore[index]
    assert summary["records"][0]["outcome"] == "BLOCKED"  # type: ignore[index]
    assert summary["records"][0]["reason_code"] == "REQUIRED_PLAN_EVIDENCE"  # type: ignore[index]


def test_health_report_is_unknown_without_reads_and_healthy_only_for_exact_bytes() -> None:
    manifest = b'plain canonical manifest bytes'
    object_bytes = b'published content sample'
    object_sha = hashlib.sha256(object_bytes).hexdigest()
    manifest_sha = hashlib.sha256(manifest).hexdigest()
    unknown = verify_content_health(manifest, expected_manifest_sha256=manifest_sha,
                                    expected_objects={"packs/level-01.scrubpack": object_sha}, observed_objects=None)
    assert unknown["status"] == "UNKNOWN"
    assert verify_content_health(None, expected_manifest_sha256=manifest_sha,
                                 expected_objects={"packs/level-01.scrubpack": object_sha}, observed_objects={})["status"] == "UNKNOWN"
    healthy = verify_content_health(manifest, expected_manifest_sha256=manifest_sha,
                                    expected_objects={"packs/level-01.scrubpack": object_sha},
                                    observed_objects={"packs/level-01.scrubpack": object_bytes})
    assert healthy["status"] == "HEALTHY"
    mismatch = verify_content_health(manifest, expected_manifest_sha256=manifest_sha,
                                     expected_objects={"packs/level-01.scrubpack": object_sha},
                                     observed_objects={"packs/level-01.scrubpack": b"different"})
    assert mismatch["status"] == "FAIL"
    assert mismatch["objects"][0]["disposition"] == "HASH_MISMATCH"  # type: ignore[index]


def test_error_records_and_jsonl_schema_do_not_accept_free_form_secret_or_pii_fields() -> None:
    record = _record(kind="ERROR", outcome="FAILED", reason_code="PROVIDER_TIMEOUT")
    value = json.loads(render_jsonl((record,)))
    assert set(value) == {"schema", "schema_version", "operation_id", "occurred_at", "kind", "environment",
                          "outcome", "reason_code", "batch_id", "content_version", "manifest_sha256",
                          "expected_object_sha256", "observed_object_sha256"}
    assert "message" not in value and "email" not in value and "credential" not in value
    with pytest.raises(OperationsEvidenceError, match="secret-like"):
        _record(operation_id="api_key-secret")
    with pytest.raises(OperationsEvidenceError, match="timezone"):
        _record(occurred_at="2026-10-14T08:15:00")


def test_backup_export_verifies_all_bytes_before_returning_recovered_objects() -> None:
    objects = {"manifests/staging.json": b"manifest", "packs/level-11.scrubpack": b"pack-bytes"}
    bundle = export_recovery_bundle(objects)
    assert restore_recovery_bundle(bundle) == objects
    document = json.loads(bundle)
    document["objects"][1]["bytes_b64"] = "cGFjaw=="
    tampered = json.dumps(document, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    with pytest.raises(OperationsEvidenceError, match="bundle hash"):
        restore_recovery_bundle(tampered)
    with pytest.raises(OperationsEvidenceError, match="unsafe path"):
        export_recovery_bundle({"../escape": b"no"})


def test_operational_runbook_keeps_live_restore_as_an_owner_gate() -> None:
    report = (Path(__file__).resolve().parents[2] / "docs/operations/CONTENT_PLATFORM_INCIDENT_RECOVERY_RUNBOOK_V01.md").read_text(encoding="utf-8")
    assert "UNKNOWN" in report
    assert "does not write, upload, activate, or replace" in report
    assert "explicit owner authorization" in report
    assert "no live-provider action authorization" in report
