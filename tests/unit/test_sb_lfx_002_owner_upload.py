from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import subprocess
import zlib

import scrubbots_pixel_factory.owner_upload as owner_upload


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "level_factory"
LAUNCHER = FACTORY / "scripts" / "factory_core_launcher.py"
GATEWAY = FACTORY / "scripts" / "factory_core_gateway.gd"
IMPORT_SCRIPT = FACTORY / "scripts" / "factory_studio_import.gd"
WORKSPACE = FACTORY / "scripts" / "factory_studio_workspace_page.gd"
INTEGRATION = FACTORY / "tests" / "factory_studio_import_integration_suite.gd"


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def _rgba_png(width: int, height: int, pixels: bytes) -> bytes:
    rows = b"".join(b"\x00" + pixels[row * width * 4 : (row + 1) * width * 4] for row in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header) + _chunk(b"IDAT", zlib.compress(rows, 9)) + _chunk(b"IEND", b"")


def test_owner_upload_preserves_bytes_and_is_content_addressed(tmp_path: Path, monkeypatch) -> None:
    destination_root = tmp_path / "owner-uploads"
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda: destination_root)
    source = tmp_path / "owner.png"
    raw = _rgba_png(3, 2, bytes((255, 0, 0, 255, 0, 255, 0, 255, 0, 0, 255, 255, 20, 30, 40, 255, 50, 60, 70, 255, 80, 90, 100, 255)))
    source.write_bytes(raw)
    before = source.read_bytes()

    imported = owner_upload.import_owner_upload(source)
    assert imported["state"] == "IMPORTED"
    assert imported["origin"] == "OWNER_UPLOAD"
    assert imported["status"] == "SOURCE_ONLY"
    assert imported["validation_state"] == "UNVALIDATED"
    assert imported["source_sha256"] == hashlib.sha256(raw).hexdigest()
    assert imported["byte_length"] == len(raw)
    assert (destination_root / imported["source_id"] / "source.png").read_bytes() == raw
    assert source.read_bytes() == before
    record = json.loads((destination_root / imported["source_id"] / "source.json").read_text(encoding="utf-8"))
    assert record["immutable_relative_path"] == f"owner-uploads/{imported['source_id']}/source.png"
    assert record["source_id"] == imported["source_id"]

    renamed = tmp_path / "different-display-name.png"
    renamed.write_bytes(raw)
    already = owner_upload.import_owner_upload(renamed)
    assert already["state"] == "ALREADY_IMPORTED"
    assert already["source_id"] == imported["source_id"]
    assert (destination_root / imported["source_id"] / "source.json").read_bytes() == (destination_root / imported["source_id"] / "source.json").read_bytes()


def test_owner_upload_collision_and_corruption_fail_closed(tmp_path: Path, monkeypatch) -> None:
    destination_root = tmp_path / "owner-uploads"
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda: destination_root)
    first = tmp_path / "same-name.png"
    second = tmp_path / "same-name-copy.png"
    first_raw = _rgba_png(2, 2, bytes((255, 0, 0, 255)) * 4)
    second_raw = _rgba_png(2, 2, bytes((0, 0, 255, 255)) * 4)
    first.write_bytes(first_raw)
    second.write_bytes(second_raw)
    first_result = owner_upload.import_owner_upload(first)
    second_result = owner_upload.import_owner_upload(second)
    assert first_result["state"] == second_result["state"] == "IMPORTED"
    assert first_result["source_id"] != second_result["source_id"]
    assert (destination_root / first_result["source_id"] / "source.png").read_bytes() == first_raw

    record_path = destination_root / first_result["source_id"] / "source.json"
    original_record = record_path.read_bytes()
    record_path.write_text("{\"corrupt\":true}", encoding="utf-8")
    rejected = owner_upload.import_owner_upload(first)
    assert rejected["state"] == "ERROR"
    assert "source" in rejected["error"].lower()
    record_path.write_bytes(original_record)

    corrupt = tmp_path / "corrupt.png"
    corrupt.write_bytes(b"not a png")
    unsupported = owner_upload.import_owner_upload(corrupt)
    assert unsupported["state"] == "ERROR"
    assert len(list(destination_root.glob("owner-upload-*"))) == 2


def test_owner_upload_operation_and_import_surface_are_bounded() -> None:
    owner_source = (ROOT / "src" / "scrubbots_pixel_factory" / "owner_upload.py").read_text(encoding="utf-8").lower()
    launcher = LAUNCHER.read_text(encoding="utf-8").lower()
    gateway = GATEWAY.read_text(encoding="utf-8").lower()
    import_source = IMPORT_SCRIPT.read_text(encoding="utf-8").lower()
    workspace = WORKSPACE.read_text(encoding="utf-8").lower()
    assert 'owner_upload_origin = "owner_upload"' in owner_source
    assert 'owner_upload_status = "source_only"' in owner_source
    assert 'owner_upload_validation_state = "unvalidated"' in owner_source
    assert "owner-upload-" in owner_source
    assert "semanticrawartifact.from_local_file" in owner_source
    for forbidden in ("normalize_semantic_artifact", "palette_snap", "compile_level_art", "evaluate_grid", "qualitypolicy", "httprequest", "http://", "https://", "api_key", "credential", "tasks.md"):
        assert forbidden not in owner_source
    assert '"owner-upload"' in launcher and "import_owner_upload" in launcher
    assert "run_owner_import" in gateway and "owner-upload" in gateway
    assert "filedialog" in import_source and "set_source_path" in import_source
    assert "source only" in import_source and "sb-lfx-004" in import_source
    assert "operationsimport" in workspace
    assert INTEGRATION.is_file()


def test_real_import_surface_integration_passes_headlessly() -> None:
    result = subprocess.run(
        [
            "godot_console.exe",
            "--headless",
            "--path",
            "level_factory",
            "--script",
            "res://tests/factory_studio_import_integration_suite.gd",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "SB-LFX-002-C001 OWNER_UPLOAD import integration PASS" in output
    for forbidden in ("Parse Error", "SCRIPT ERROR", "No such file or directory", "Missing resource"):
        assert forbidden not in output
