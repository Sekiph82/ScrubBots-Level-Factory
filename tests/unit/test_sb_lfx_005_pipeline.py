from __future__ import annotations

from pathlib import Path

from scrubbots_pixel_factory import owner_upload, studio_extensions as studio
from scrubbots_pixel_factory.output.png import encode_logical_png


def test_pipeline_records_truthful_owner_upload_stop_and_preserves_source(tmp_path: Path, monkeypatch) -> None:
    repository = tmp_path / "repository"
    source_root = repository / "level_factory/output/owner-uploads"
    evidence_root = repository / "level_factory/output/studio-extensions"
    source_root.mkdir(parents=True)
    evidence_root.mkdir(parents=True)
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda: source_root)
    monkeypatch.setattr(owner_upload, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "owner_upload_root", lambda: source_root)
    monkeypatch.setattr(studio, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "extensions_root", lambda: evidence_root)
    source_path = tmp_path / "pipeline.png"
    source_path.write_bytes(encode_logical_png(20, 20, ["C01", "C02", "C03", "C04"] * 100))
    imported = owner_upload.import_owner_upload(source_path)
    source_id = str(imported["source_id"])
    source_bytes = (owner_upload.owner_upload_root() / source_id / "source.png").read_bytes()
    try:
        run = studio.run_pipeline(source_id=source_id)
        assert run["schema"] == "scrubbots-studio-pipeline-run"
        dispositions = {stage["stage"]: stage["disposition"] for stage in run["stages"]}
        assert dispositions["SOURCE"] == "PASS"
        assert run["disposition"] == "READY"
        assert dispositions["CANDIDATE"] == "PASS"
        assert dispositions["SOLVE"] == "PASS"
        assert dispositions["DIFFICULTY"] == "PASS"
        assert dispositions["QA"] == "PASS"
        assert (owner_upload.owner_upload_root() / source_id / "source.png").read_bytes() == source_bytes
    finally:
        root = owner_upload.owner_upload_root() / source_id
        for child in root.iterdir(): child.unlink()
        root.rmdir()
        for path in (studio.extensions_root() / "validation").glob(f"{source_id}-*.json"):
            path.unlink()
        for path in (studio.extensions_root() / "pipelines").glob("pipeline-*.json"):
            path.unlink()
