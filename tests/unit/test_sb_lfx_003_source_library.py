from __future__ import annotations

import json
from pathlib import Path
import shutil

from scrubbots_pixel_factory import owner_upload, studio_extensions
from scrubbots_pixel_factory.output.png import encode_logical_png


def _fixture(path: Path, first: str, second: str) -> None:
    colors = [first, second, "C05"]
    cells = [colors[min(x // 18, 2)] for _y in range(52) for x in range(52)]
    path.write_bytes(encode_logical_png(52, 52, cells))


def test_source_library_exposes_only_current_final_and_preserves_historical_records(tmp_path: Path, monkeypatch) -> None:
    repository = tmp_path / "repository"
    final_root = repository / "data/output/Pixellab/Final"
    final_root.mkdir(parents=True)
    source_root = repository / "level_factory/output/owner-uploads"
    evidence_root = repository / "level_factory/output/studio-extensions"
    source_root.mkdir(parents=True)
    evidence_root.mkdir(parents=True)
    monkeypatch.setattr(owner_upload, "_repository_root", lambda: repository)
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda _root=None: source_root)
    monkeypatch.setattr(studio_extensions, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio_extensions, "owner_upload_root", lambda _root=None: source_root)
    monkeypatch.setattr(studio_extensions, "extensions_root", lambda: evidence_root)

    first_path = final_root / "current.png"
    second_path = tmp_path / "legacy" / "retired.png"
    second_path.parent.mkdir()
    _fixture(first_path, "C01", "C02")
    _fixture(second_path, "C03", "C04")
    first = owner_upload.import_owner_upload(first_path)
    second = owner_upload.import_owner_upload(second_path)
    assert first["state"] == second["state"] == "IMPORTED"
    first_id, second_id = str(first["source_id"]), str(second["source_id"])
    first_source = source_root / first_id / "source.png"
    first_record = source_root / first_id / "source.json"
    before_source, before_record = first_source.read_bytes(), first_record.read_bytes()
    try:
        view = studio_extensions.library_refresh(repository_root=repository)
        assert [item["source_id"] for item in view["sources"]] == [first_id], view["invalid_sources"]
        assert [item["source_id"] for item in view["historical_sources"]] == [second_id]

        saved = studio_extensions.save_library_metadata(first_id, "Robot One", ["owner", "blueprint"])
        assert saved["catalog"]["source_id"] == first_id
        assert first_source.read_bytes() == before_source
        assert first_record.read_bytes() == before_record
        refreshed = studio_extensions.library_refresh(repository_root=repository)
        selected = next(item for item in refreshed["sources"] if item["source_id"] == first_id)
        assert selected["catalog"]["label"] == "Robot One"
        assert selected["catalog"]["tags"] == ["blueprint", "owner"]

        first_record.write_text(json.dumps({"corrupt": True}), encoding="utf-8")
        corrupted = studio_extensions.library_refresh(repository_root=repository)
        assert any(item["source_id"] == first_id for item in corrupted["invalid_sources"])
        assert all(item["source_id"] != first_id for item in corrupted["sources"])
    finally:
        shutil.rmtree(repository)
