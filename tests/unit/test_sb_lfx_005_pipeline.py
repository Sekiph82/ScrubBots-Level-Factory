from __future__ import annotations

from pathlib import Path

from scrubbots_pixel_factory.owner_upload import import_owner_upload, owner_upload_root
from scrubbots_pixel_factory.output.png import encode_logical_png
from scrubbots_pixel_factory.studio_extensions import extensions_root, run_pipeline


def test_pipeline_records_truthful_owner_upload_stop_and_preserves_source(tmp_path: Path) -> None:
    source_path = tmp_path / "pipeline.png"
    source_path.write_bytes(encode_logical_png(20, 20, ["C01", "C02", "C03", "C04"] * 100))
    imported = import_owner_upload(source_path)
    source_id = str(imported["source_id"])
    source_bytes = (owner_upload_root() / source_id / "source.png").read_bytes()
    try:
        run = run_pipeline(source_id=source_id)
        assert run["schema"] == "scrubbots-studio-pipeline-run"
        dispositions = {stage["stage"]: stage["disposition"] for stage in run["stages"]}
        assert dispositions["SOURCE"] == "PASS"
        assert dispositions["CANDIDATE"] == "NOT_AVAILABLE"
        assert dispositions["SOLVE"] == "NOT_AVAILABLE"
        assert dispositions["DIFFICULTY"] == "NOT_AVAILABLE"
        assert dispositions["REVIEW"] == "NOT_AVAILABLE"
        assert (owner_upload_root() / source_id / "source.png").read_bytes() == source_bytes
    finally:
        root = owner_upload_root() / source_id
        for child in root.iterdir(): child.unlink()
        root.rmdir()
        for path in (extensions_root() / "validation").glob(f"{source_id}-*.json"):
            path.unlink()
        for path in (extensions_root() / "pipelines").glob("pipeline-*.json"):
            path.unlink()
