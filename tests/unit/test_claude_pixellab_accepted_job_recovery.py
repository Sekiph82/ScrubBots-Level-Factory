"""Owner 2026-11-10: a row accepted and charged by PixelLab but lost to a network error
must be fetched again (read-only) on the next Run Batch, never resubmitted."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "level_factory" / "scripts"))
import factory_core_launcher as launcher  # noqa: E402


def _record(job_root: Path, operation_id: str, **fields) -> Path:
    record = {"schema": "scrubbots-pixellab-pro-4x4-job-v1", "transport": "PIXELLAB_REMOTE_MCP_HTTP",
              "operation_id": operation_id, "request_sha256": "r" + operation_id, "paid_submission_possible": True,
              "width": 56, "height": 56, "max_colors": 12, "seed": 7, **fields}
    path = job_root / f"{operation_id}.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    return path


def test_network_error_jobs_are_fetched_read_only_and_completed(tmp_path: Path, monkeypatch) -> None:
    job_root = tmp_path / "pixellab-jobs"
    job_root.mkdir()
    lost = _record(job_root, "lost", state="MCP_NETWORK_ERROR", job_id="job-lost")
    _record(job_root, "done", state="SOURCES_IMPORTED_NOT_READY", job_id="job-done", atlas_sha256="a" * 64)
    _record(job_root, "unaccepted", state="SUBMISSION_UNKNOWN")             # no job ID: owner review, not auto
    _record(job_root, "rejected", state="MCP_HTTP_ERROR", job_id=None)
    fetched: list[dict] = []

    def fake_generate(**kwargs):
        fetched.append(kwargs)
        return SimpleNamespace(job_id=kwargs["resume_job_id"], atlas_png=b"png", mcp_request_count=3)

    extensions = SimpleNamespace(extensions_root=lambda: tmp_path, generate_pixellab_pro_4x4_atlas_mcp=fake_generate)

    def fake_finish(record, persist_job, generated, **_kwargs):
        record.update({"state": "SOURCES_IMPORTED_NOT_READY", "atlas_sha256": "b" * 64})
        persist_job()
        return {"state": "SOURCES_IMPORTED_NOT_READY", "pass_count": 16, "atlas_path": "PX-ATLAS-000099.png"}

    monkeypatch.setattr(launcher, "_finish_pixellab_atlas_job", fake_finish)

    recovered = launcher._recover_accepted_pixellab_jobs(extensions)

    assert [item["operation_id"] for item in recovered] == ["lost"]
    assert [call["resume_job_id"] for call in fetched] == ["job-lost"]   # resume only: no create_image_pro
    saved = json.loads(lost.read_text(encoding="utf-8"))
    assert saved["state"] == "SOURCES_IMPORTED_NOT_READY" and saved["recovered_from_state"] == "MCP_NETWORK_ERROR"
    assert launcher._recover_accepted_pixellab_jobs(extensions) == []      # second run: nothing left


def test_failed_recovery_stays_recoverable_and_live_polling_is_left_alone(tmp_path: Path) -> None:
    job_root = tmp_path / "pixellab-jobs"
    job_root.mkdir()
    lost = _record(job_root, "lost", state="POLL_TIMEOUT", job_id="job-lost")
    _record(job_root, "live", state="POLLING", job_id="job-live")

    def offline(**_kwargs):
        raise OSError("still offline")

    extensions = SimpleNamespace(extensions_root=lambda: tmp_path, generate_pixellab_pro_4x4_atlas_mcp=offline)
    recovered = launcher._recover_accepted_pixellab_jobs(extensions)

    assert [(item["operation_id"], item["state"]) for item in recovered] == [("lost", "RECOVERY_DEFERRED")]
    assert json.loads(lost.read_text(encoding="utf-8"))["state"] == "POLL_TIMEOUT"
