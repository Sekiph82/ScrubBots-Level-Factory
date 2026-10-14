from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from scrubbots_content_pipeline import cli
from scrubbots_content_pipeline.operations import (
    OperationRecord,
    OperationsEvidenceError,
    write_local_operation_evidence,
)


def test_dry_run_can_emit_local_secret_free_operation_evidence(monkeypatch, tmp_path, capsys) -> None:
    target = tmp_path / "operations-20261014"
    monkeypatch.setattr("sys.argv", ["scrubbots-content-pipeline", "--dry-run", "--environment", "staging",
                                      "--operations-dir", str(target)])

    assert cli.main() == 1
    report = json.loads(capsys.readouterr().out)
    assert report["remote_mutation_performed"] is False
    rows = [json.loads(line) for line in (target / "operations.jsonl").read_text(encoding="utf-8").splitlines()]
    summary = json.loads((target / "weekly-summary.json").read_text(encoding="utf-8"))
    assert len(rows) == 1
    assert rows[0]["kind"] == "ERROR"
    assert rows[0]["environment"] == "STAGING"
    assert rows[0]["outcome"] == "BLOCKED"
    assert rows[0]["reason_code"] == "REQUIRED_PLAN_EVIDENCE"
    assert summary["record_count"] == 1
    assert "token" not in json.dumps(rows).lower()


def test_operation_evidence_refuses_existing_owner_directory(monkeypatch, tmp_path) -> None:
    target = tmp_path / "existing"
    target.mkdir()
    sentinel = target / "owner.txt"
    sentinel.write_text("preserve", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["scrubbots-content-pipeline", "--dry-run", "--operations-dir", str(target)])

    with pytest.raises(OperationsEvidenceError, match="new directory"):
        cli.main()
    assert sentinel.read_text(encoding="utf-8") == "preserve"


def test_cli_rejects_operation_output_outside_dry_run(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("sys.argv", ["scrubbots-content-pipeline", "--validate-only", "--operations-dir",
                                      str(tmp_path / "not-created")])
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 2
    assert not (tmp_path / "not-created").exists()


def test_failed_write_rolls_back_only_the_new_operation_directory(monkeypatch, tmp_path) -> None:
    target = tmp_path / "new-output"
    original_open = Path.open

    def fail_summary(path: Path, mode: str = "r", *args, **kwargs):
        if path.name == "weekly-summary.json":
            raise OSError("bounded synthetic write failure")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail_summary)
    record = OperationRecord("preflight-01", "2026-10-14T08:15:00Z", "ERROR", "STAGING", "BLOCKED",
                             "REQUIRED_PLAN_EVIDENCE")

    with pytest.raises(OperationsEvidenceError, match="rolled back"):
        write_local_operation_evidence(target, (record,), week_start=date(2026, 10, 14), week_end=date(2026, 10, 15))
    assert not target.exists()


@pytest.mark.parametrize("protected", [".hiveai/audits/new-evidence", ".git/objects/new-evidence", "TASKS.md"])
def test_operation_output_refuses_protected_repository_paths(tmp_path, protected) -> None:
    target = tmp_path.joinpath(*protected.split("/"))
    with pytest.raises(OperationsEvidenceError, match="protected repository control files"):
        write_local_operation_evidence(
            target,
            (),
            week_start=date(2026, 10, 14),
            week_end=date(2026, 10, 15),
        )
    assert not target.exists()
