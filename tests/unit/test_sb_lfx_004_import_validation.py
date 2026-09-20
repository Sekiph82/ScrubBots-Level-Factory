from __future__ import annotations

from pathlib import Path
import struct
import zlib

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


def _encode_rgba_png(width: int, height: int, rgba: bytes) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    rows = b"".join(b"\x00" + rgba[row * width * 4 : (row + 1) * width * 4] for row in range(height))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")


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


def test_validation_alpha_failure_and_tampered_source_or_evidence_fail_closed(tmp_path: Path) -> None:
    path = tmp_path / "semi-alpha.png"
    rgba = bytes((233, 75, 75, 128)) * (20 * 20)
    path.write_bytes(_encode_rgba_png(20, 20, rgba))
    result = import_owner_upload(path)
    source_id = str(result["source_id"])
    source_root = owner_upload_root() / source_id
    source_path = source_root / "source.png"
    record_path = source_root / "source.json"
    validation_path = extensions_root() / "validation" / f"{source_id}-{result['source_sha256']}.json"
    before_source = source_path.read_bytes()
    before_record = record_path.read_bytes()
    try:
        report = validate_owner_source(source_id)
        assert report["exact_logical_source"] is False
        assert report["alpha"]["semi_alpha_count"] == 400
        assert "ALPHA_CONTRACT" in report["structural"]["rejection_codes"]
        assert report["logical_dimension_status"] == "DERIVED_ARTIFACT_REQUIRED"
        assert source_path.read_bytes() == before_source
        assert record_path.read_bytes() == before_record

        source_path.write_bytes(before_source + b"tamper")
        try:
            try:
                validate_owner_source(source_id, persist=False)
            except Exception as exc:
                assert "source bytes" in str(exc)
            else:
                raise AssertionError("tampered source unexpectedly validated")
        finally:
            source_path.write_bytes(before_source)

        validate_owner_source(source_id)
        evidence_before = validation_path.read_bytes()
        validation_path.write_bytes(evidence_before.replace(b"ALPHA_CONTRACT", b"TAMPERED"))
        try:
            try:
                validate_owner_source(source_id)
            except Exception as exc:
                assert "immutable evidence" in str(exc)
            else:
                raise AssertionError("conflicting validation evidence was silently trusted")
        finally:
            validation_path.write_bytes(evidence_before)
        assert source_path.read_bytes() == before_source
        assert record_path.read_bytes() == before_record
    finally:
        source_path.write_bytes(before_source)
        record_path.write_bytes(before_record)
        _cleanup(source_id)
