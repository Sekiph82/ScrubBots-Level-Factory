from __future__ import annotations

from datetime import date
import hashlib
import json
from pathlib import Path

import pytest

from scrubbots_content_pipeline import cli
from scrubbots_content_pipeline.manifest_v1 import ContentManifestV1, ManifestPackV1
from scrubbots_content_pipeline.operations import (
    OperationRecord,
    OperationsEvidenceError,
    export_recovery_bundle,
    operation_record_from_manifest_observation,
    operation_record_from_object_observation,
    operation_record_from_control_receipt,
    render_jsonl,
    restore_recovery_bundle,
    verify_content_health,
    weekly_batch_summary,
)
from scrubbots_content_pipeline.one_command_publisher import (
    PublisherMode,
    PublisherRunReport,
    PublisherStage,
)
from scrubbots_content_pipeline.production_manifest_activation import (
    ProductionManifestActivationReport,
    ProductionManifestReasonCode,
    ProductionManifestReceipt,
)
from scrubbots_content_pipeline.staging_download_verify import (
    StagingDownloadReasonCode,
    StagingDownloadVerificationReceipt,
    StagingDownloadVerificationReport,
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


def test_plain_dry_run_is_deterministic_and_never_invokes_evidence_writer(monkeypatch, capsys) -> None:
    def reject_evidence_write(*args, **kwargs):
        pytest.fail("plain dry-run must not create local evidence files")

    monkeypatch.setattr(cli, "write_local_operation_evidence", reject_evidence_write)
    monkeypatch.setattr(
        "sys.argv",
        ["scrubbots-content-pipeline", "--dry-run", "--environment", "staging"],
    )

    assert cli.main() == 1
    first = capsys.readouterr().out
    assert cli.main() == 1
    second = capsys.readouterr().out

    assert first == second
    report = json.loads(first)
    assert report["accepted"] is False
    assert report["complete"] is False
    assert report["remote_mutation_performed"] is False
    assert report["target_environment"] == "staging"
    assert report["checks"] == [
        {"check_id": "required_plan_evidence", "accepted": False, "reason_code": "UNVALIDATED_PAYLOAD"}
    ]


def test_health_report_is_unknown_without_reads_and_healthy_only_for_exact_bytes() -> None:
    object_bytes = b'published content sample'
    object_sha = hashlib.sha256(object_bytes).hexdigest()
    object_key = "packs/campaign/main.scrubpack"
    manifest = ContentManifestV1(
        packs=(ManifestPackV1("campaign", 1, object_key, object_sha, len(object_bytes)),),
    ).to_json_bytes()
    manifest_sha = hashlib.sha256(manifest).hexdigest()
    unknown = verify_content_health(manifest, expected_manifest_sha256=manifest_sha,
                                    expected_objects={object_key: object_sha}, observed_objects=None)
    assert unknown["status"] == "UNKNOWN"
    assert verify_content_health(None, expected_manifest_sha256=manifest_sha,
                                 expected_objects={object_key: object_sha}, observed_objects={})["status"] == "UNKNOWN"
    healthy = verify_content_health(manifest, expected_manifest_sha256=manifest_sha,
                                    expected_objects={object_key: object_sha},
                                    observed_objects={object_key: object_bytes})
    assert healthy["status"] == "HEALTHY"
    mismatch = verify_content_health(manifest, expected_manifest_sha256=manifest_sha,
                                     expected_objects={object_key: object_sha},
                                     observed_objects={object_key: b"different"})
    assert mismatch["status"] == "FAIL"
    assert mismatch["objects"][0]["disposition"] == "HASH_MISMATCH"  # type: ignore[index]
    assert verify_content_health(manifest, expected_manifest_sha256="0" * 64,
                                 expected_objects={object_key: object_sha},
                                 observed_objects={object_key: object_bytes})["reason"] == "MANIFEST_HASH_MISMATCH"
    malformed = b"not a manifest"
    assert verify_content_health(malformed, expected_manifest_sha256=hashlib.sha256(malformed).hexdigest(),
                                 expected_objects={object_key: object_sha},
                                 observed_objects={object_key: object_bytes})["reason"] == "INVALID_MANIFEST"
    assert verify_content_health(manifest, expected_manifest_sha256=manifest_sha,
                                 expected_objects={object_key: "0" * 64},
                                 observed_objects={object_key: object_bytes})["reason"] == "MANIFEST_OBJECT_SET_MISMATCH"


def test_error_records_and_jsonl_schema_do_not_accept_free_form_secret_or_pii_fields() -> None:
    record = _record(kind="ERROR", outcome="FAILED", reason_code="PROVIDER_TIMEOUT")
    value = json.loads(render_jsonl((record,)))
    assert value["schema_version"] == 2
    assert set(value) == {"schema", "schema_version", "operation_id", "occurred_at", "kind", "environment",
                          "outcome", "reason_code", "batch_id", "target_id", "content_version", "manifest_sha256",
                          "expected_object_sha256", "observed_object_sha256"}
    assert "message" not in value and "email" not in value and "credential" not in value
    with pytest.raises(OperationsEvidenceError, match="secret-like"):
        _record(operation_id="api_key-secret")
    with pytest.raises(OperationsEvidenceError, match="timezone"):
        _record(occurred_at="2026-10-14T08:15:00")


def test_staging_and_production_versions_require_and_bind_observed_manifest_bytes() -> None:
    observed = b'{"content_version":7,"disabled_levels":[],"levels":[],"minimum_game_version":"0.0.0","packs":[],"schedules":[],"schema":"scrubbots.content.manifest.v1","schema_version":1}'
    staging = operation_record_from_manifest_observation(
        observed,
        environment="STAGING",
        operation_id="version-staging-01",
        occurred_at="2026-10-14T08:15:00Z",
    )
    production = operation_record_from_manifest_observation(
        observed,
        environment="PRODUCTION",
        operation_id="version-production-01",
        occurred_at="2026-10-14T08:16:00Z",
    )

    assert (staging.kind, staging.environment, staging.content_version) == ("STAGING_VERSION", "STAGING", 7)
    assert (production.kind, production.environment, production.content_version) == ("PRODUCTION_VERSION", "PRODUCTION", 7)
    assert staging.manifest_sha256 == production.manifest_sha256 == hashlib.sha256(observed).hexdigest()
    summary = weekly_batch_summary((staging, production), date(2026, 10, 14), date(2026, 10, 15))
    assert [row["content_version"] for row in summary["records"]] == [7, 7]  # type: ignore[index]

    for unobserved in (None, b"not a manifest"):
        with pytest.raises(OperationsEvidenceError):
            operation_record_from_manifest_observation(
                unobserved,
                environment="STAGING",
                operation_id="version-unobserved",
                occurred_at="2026-10-14T08:17:00Z",
            )
    with pytest.raises(OperationsEvidenceError, match="match its environment"):
        OperationRecord("version-mismatch", "2026-10-14T08:15:00Z", "STAGING_VERSION", "PRODUCTION",
                        "COMPLETED", "VERSION_OBSERVED", content_version=7,
                        manifest_sha256=hashlib.sha256(observed).hexdigest())
    with pytest.raises(OperationsEvidenceError, match="observed manifest version and digest"):
        OperationRecord("version-missing", "2026-10-14T08:15:00Z", "STAGING_VERSION", "STAGING",
                        "COMPLETED", "VERSION_OBSERVED")


def test_publisher_verified_readbacks_bridge_to_staging_and_production_version_records() -> None:
    observed = b'{"content_version":7,"disabled_levels":[],"levels":[],"minimum_game_version":"0.0.0","packs":[],"schedules":[],"schema":"scrubbots.content.manifest.v1","schema_version":1}'
    digest = hashlib.sha256(observed).hexdigest()
    staging_receipt = StagingDownloadVerificationReceipt(
        "1.0", observed, digest, len(observed), 7, "manifests/current.json", "staging",
        "staging:default", "provider", "1.0", "1.0", "capability", "1.0", "1.0.0",
        (), (), (), (), ("manifest_sha256",),
    )
    staging = StagingDownloadVerificationReport(
        True, StagingDownloadReasonCode.VERIFIED, staging_receipt, None, True, (),
    )
    production_receipt = ProductionManifestReceipt(
        manifest_bytes=observed,
        manifest_sha256=digest,
        content_version=7,
        production_target_id="production:default",
        manifest_object_key="manifests/current.json",
        provider_id="provider",
        prior_manifest_sha256=None,
        prior_content_version=None,
        compatibility=object(),
        reference_validation=object(),
        packs=(),
        history_record=object(),
        manifest_history=object(),
        history_tip_sha256="a" * 64,
        promotion_pending_event_digest="b" * 64,
        production_promoted_event=object(),
        game_commit="c" * 40,
    )
    production = ProductionManifestActivationReport(
        True, ProductionManifestReasonCode.ACTIVATED, True, production_receipt, object(),
    )
    report = PublisherRunReport(
        True, PublisherMode.PRODUCTION, "ACTIVATED", PublisherStage.CURRENT_STATE_FENCE, (),
        staging_download=staging, production_activation=production,
    )

    records = report.observed_version_operation_records(
        operation_id_prefix="publish-01", occurred_at="2026-11-06T01:00:00Z",
    )

    assert [(item.kind, item.environment, item.content_version, item.manifest_sha256) for item in records] == [
        ("STAGING_VERSION", "STAGING", 7, digest),
        ("PRODUCTION_VERSION", "PRODUCTION", 7, digest),
    ]
    assert [item.operation_id for item in records] == ["publish-01:staging", "publish-01:production"]
    summary = weekly_batch_summary(records, date(2026, 11, 2), date(2026, 11, 9))
    assert [row["content_version"] for row in summary["records"]] == [7, 7]  # type: ignore[index]


def test_publisher_version_bridge_ignores_unverified_reads_and_rejects_receipt_byte_drift() -> None:
    observed = b'{"content_version":7,"disabled_levels":[],"levels":[],"minimum_game_version":"0.0.0","packs":[],"schedules":[],"schema":"scrubbots.content.manifest.v1","schema_version":1}'
    digest = hashlib.sha256(observed).hexdigest()
    receipt = StagingDownloadVerificationReceipt(
        "1.0", observed, digest, len(observed), 7, "manifests/current.json", "staging",
        "staging:default", "provider", "1.0", "1.0", "capability", "1.0", "1.0.0",
        (), (), (), (), ("manifest_sha256",),
    )
    unverified = StagingDownloadVerificationReport(
        False, StagingDownloadReasonCode.MANIFEST_READ_FAILED, None, None, False, (),
    )
    failed_report = PublisherRunReport(
        False, PublisherMode.STAGING_ONLY, "MANIFEST_READ_FAILED", PublisherStage.STAGING_DOWNLOAD_VERIFY, (),
        staging_download=unverified,
    )
    assert failed_report.observed_version_operation_records(
        operation_id_prefix="publish-02", occurred_at="2026-11-06T01:00:00Z",
    ) == ()

    already_current = ProductionManifestActivationReport(
        True, ProductionManifestReasonCode.ALREADY_CURRENT, False, None, object(),
    )
    already_current_report = PublisherRunReport(
        True, PublisherMode.PRODUCTION, "ALREADY_CURRENT", PublisherStage.CURRENT_STATE_FENCE, (),
        production_activation=already_current,
    )
    assert already_current_report.observed_version_operation_records(
        operation_id_prefix="publish-02-current", occurred_at="2026-11-06T01:00:00Z",
    ) == ()

    mismatched_receipt = StagingDownloadVerificationReceipt(
        "1.0", observed, "0" * 64, len(observed), 7, "manifests/current.json", "staging",
        "staging:default", "provider", "1.0", "1.0", "capability", "1.0", "1.0.0",
        (), (), (), (), ("manifest_sha256",),
    )
    mismatched = StagingDownloadVerificationReport(
        True, StagingDownloadReasonCode.VERIFIED, mismatched_receipt, None, True, (),
    )
    mismatched_report = PublisherRunReport(
        True, PublisherMode.STAGING_ONLY, "STAGING_VERIFIED", PublisherStage.STAGING_DOWNLOAD_VERIFY, (),
        staging_download=mismatched,
    )
    with pytest.raises(OperationsEvidenceError, match="disagrees with its exact manifest bytes"):
        mismatched_report.observed_version_operation_records(
            operation_id_prefix="publish-03", occurred_at="2026-11-06T01:00:00Z",
        )


def test_object_verification_records_only_exact_observed_hashes() -> None:
    expected_bytes = b"expected object bytes"
    expected_sha256 = hashlib.sha256(expected_bytes).hexdigest()
    matched = operation_record_from_object_observation(
        expected_sha256,
        expected_bytes,
        environment="STAGING",
        operation_id="object-match-01",
        occurred_at="2026-10-14T09:00:00Z",
    )
    mismatched = operation_record_from_object_observation(
        expected_sha256,
        b"different observed bytes",
        environment="PRODUCTION",
        operation_id="object-mismatch-01",
        occurred_at="2026-10-14T09:01:00Z",
    )

    assert (matched.outcome, matched.expected_object_sha256, matched.observed_object_sha256) == (
        "MATCH", expected_sha256, expected_sha256,
    )
    assert mismatched.outcome == "MISMATCH"
    assert mismatched.expected_object_sha256 == expected_sha256
    assert mismatched.observed_object_sha256 == hashlib.sha256(b"different observed bytes").hexdigest()
    report = weekly_batch_summary((matched, mismatched), date(2026, 10, 14), date(2026, 10, 15))
    assert report["recorded_object_verifications_marked_match"] == 1

    with pytest.raises(OperationsEvidenceError, match="explicitly observed"):
        operation_record_from_object_observation(
            expected_sha256,
            None,
            environment="STAGING",
            operation_id="object-unknown-01",
            occurred_at="2026-10-14T09:02:00Z",
        )
    with pytest.raises(OperationsEvidenceError, match="must compare observed digests"):
        OperationRecord(
            "object-invalid-outcome",
            "2026-10-14T09:03:00Z",
            "OBJECT_VERIFY",
            "STAGING",
            "COMPLETED",
            "HASH_MATCH",
            expected_object_sha256=expected_sha256,
            observed_object_sha256=expected_sha256,
        )


def test_m17_control_receipts_map_to_local_prepared_change_records_only() -> None:
    from dataclasses import replace

    from scrubbots_content_pipeline.m17_release_controls import ReceiptOperation, make_control_receipt

    def receipt(operation: ReceiptOperation, outcome: str):
        return make_control_receipt(
            actor_ref="owner-01",
            operation=operation,
            occurred_at_utc="2026-10-14T10:00:00Z",
            target_id="target-01",
            current_version=4,
            next_version=5,
            prior_manifest_sha256="a" * 64,
            new_manifest_sha256="b" * 64,
            pack_hashes=(("campaign", "c" * 64),),
            approval_id="approval-01",
            provider_record_sha256="d" * 64,
            outcome=outcome,
        )

    cases = (
        (ReceiptOperation.DISABLE, "PREPARED", "DISABLE", "PREPARED", "DISABLE_PREPARED"),
        (ReceiptOperation.REENABLE, "PREPARED", "DISABLE", "PREPARED", "REENABLE_PREPARED"),
        (ReceiptOperation.ROLLBACK, "PREPARED", "ROLLBACK", "PREPARED", "ROLLBACK_PREPARED"),
        (ReceiptOperation.SCHEDULE, "INTENT_PERSISTED", "SCHEDULE", "PREPARED", "SCHEDULE_INTENT_PREPARED"),
        (ReceiptOperation.CANCEL_SCHEDULE, "INTENT_CANCELLED", "SCHEDULE_CANCEL", "COMPLETED", "SCHEDULE_CANCEL_COMPLETED"),
    )
    for operation, receipt_outcome, kind, outcome, reason in cases:
        record = operation_record_from_control_receipt(receipt(operation, receipt_outcome),
                                                        operation_id=f"control-{operation.value.lower()}")
        assert (record.kind, record.environment, record.outcome, record.reason_code) == (
            kind, "LOCAL", outcome, reason,
        )
        assert (record.target_id, record.content_version, record.manifest_sha256) == (
            "target-01", 5, "b" * 64,
        )

    good = receipt(ReceiptOperation.DISABLE, "PREPARED")
    with pytest.raises(OperationsEvidenceError):
        operation_record_from_control_receipt(replace(good, target_id="tampered-target"),
                                              operation_id="control-tampered")
    with pytest.raises(OperationsEvidenceError, match="not an auditable CP08 change"):
        operation_record_from_control_receipt(receipt(ReceiptOperation.PUBLISH, "PREPARED"),
                                              operation_id="control-publish")


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


def test_backup_restore_rejects_boolean_schema_version_even_with_valid_bundle_hash() -> None:
    document = json.loads(export_recovery_bundle({"packs/level.scrubpack": b"verified bytes"}))
    document["schema_version"] = True
    body = {key: value for key, value in document.items() if key != "bundle_sha256"}
    document["bundle_sha256"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    tampered_schema = json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"

    with pytest.raises(OperationsEvidenceError, match="supported exact schema"):
        restore_recovery_bundle(tampered_schema)


def test_operational_runbook_keeps_live_restore_as_an_owner_gate() -> None:
    report = (Path(__file__).resolve().parents[2] / "docs/operations/CONTENT_PLATFORM_INCIDENT_RECOVERY_RUNBOOK_V01.md").read_text(encoding="utf-8")
    assert "UNKNOWN" in report
    assert "does not write, upload, activate, or replace" in report
    assert "explicit owner authorization" in report
    assert "no live-provider action authorization" in report
