from __future__ import annotations

from pathlib import Path

from scrubbots_pixel_factory.owner_upload import import_owner_upload, owner_upload_root
from scrubbots_pixel_factory.output.png import _encode_rgb_png, encode_logical_png
from scrubbots_pixel_factory.studio_extensions import extensions_root, validate_owner_source


def _cleanup(source_id: str) -> None:
    root = owner_upload_root() / source_id
    if root.exists():
        for child in root.iterdir(): child.unlink()
        root.rmdir()
    for path in (extensions_root() / "validation").glob(f"{source_id}-*.json"):
        path.unlink()


def test_validation_reports_exact_logical_facts_without_mutating_owner_source(tmp_path: Path) -> None:
    path = tmp_path / "logical.png"
    path.write_bytes(encode_logical_png(20, 20, ["C01", "C02", "C03", "C04"] * 100))
    result = import_owner_upload(path)
    source_id = str(result["source_id"])
    source_path = owner_upload_root() / source_id / "source.png"
    before = source_path.read_bytes()
    try:
        report = validate_owner_source(source_id)
        assert report["exact_logical_source"] is True
        assert report["legal_logical_dimensions"] is True
        assert report["palette"]["foreign_color_count"] == 0
        assert report["alpha"]["semi_alpha_count"] == 0
        assert source_path.read_bytes() == before
        assert report["claims"]["owner_acceptance"].startswith("NOT AVAILABLE")
    finally:
        _cleanup(source_id)


def test_validation_reports_derived_artifact_required_for_foreign_and_illegal_input(tmp_path: Path) -> None:
    path = tmp_path / "foreign.png"
    raw = bytes([255, 0, 255] * (19 * 20))
    path.write_bytes(_encode_rgb_png(19, 20, raw))
    result = import_owner_upload(path)
    source_id = str(result["source_id"])
    try:
        report = validate_owner_source(source_id)
        assert report["exact_logical_source"] is False
        assert report["logical_dimension_status"] == "DERIVED_ARTIFACT_REQUIRED"
        assert report["palette"]["foreign_color_count"] == 380
        assert "CELL_MAJORITY_V1" in report["policies"].values()
        assert "PALETTE_SNAP_V1" in report["policies"].values()
    finally:
        _cleanup(source_id)
