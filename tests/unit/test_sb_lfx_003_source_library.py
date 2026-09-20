from __future__ import annotations

import json
from pathlib import Path

from scrubbots_pixel_factory.owner_upload import import_owner_upload, owner_upload_root
from scrubbots_pixel_factory.output.png import encode_logical_png
from scrubbots_pixel_factory.studio_extensions import library_refresh, save_library_metadata


def _fixture(path: Path, first: str, second: str) -> None:
    colors = [first, second]
    cells = [colors[index % 2] for index in range(20 * 20)]
    path.write_bytes(encode_logical_png(20, 20, cells))


def test_source_library_reverifies_sources_and_persists_only_bound_catalog_metadata(tmp_path: Path) -> None:
    first_path = tmp_path / "same.png"
    second_path = tmp_path / "other.png"
    _fixture(first_path, "C01", "C02")
    _fixture(second_path, "C03", "C04")
    first = import_owner_upload(first_path)
    second = import_owner_upload(second_path)
    assert first["state"] == "IMPORTED"
    assert second["state"] == "IMPORTED"
    first_id, second_id = str(first["source_id"]), str(second["source_id"])
    first_source = owner_upload_root() / first_id / "source.png"
    first_record = owner_upload_root() / first_id / "source.json"
    before_source, before_record = first_source.read_bytes(), first_record.read_bytes()
    try:
        view = library_refresh()
        assert [item["source_id"] for item in view["sources"]] == sorted([first_id, second_id])
        saved = save_library_metadata(first_id, "Robot One", ["owner", "blueprint"])
        assert saved["catalog"]["source_id"] == first_id
        assert first_source.read_bytes() == before_source
        assert first_record.read_bytes() == before_record
        refreshed = library_refresh()
        selected = next(item for item in refreshed["sources"] if item["source_id"] == first_id)
        assert selected["catalog"]["label"] == "Robot One"
        assert selected["catalog"]["tags"] == ["blueprint", "owner"]
        assert selected["owner_review"]["disposition"] == "NOT AVAILABLE"
        assert selected["palette"]["disposition"] == "NOT AVAILABLE"
        assert selected["usages"]["disposition"] == "NOT AVAILABLE"
        first_record.write_text(json.dumps({"corrupt": True}), encoding="utf-8")
        corrupted = library_refresh()
        assert any(item["source_id"] == first_id for item in corrupted["invalid_sources"])
        assert all(item["source_id"] != first_id for item in corrupted["sources"])
    finally:
        first_source.write_bytes(before_source)
        first_record.write_bytes(before_record)
        metadata = Path("level_factory/output/studio-extensions/source-library/metadata") / f"{first_id}.json"
        if metadata.exists():
            metadata.unlink()
        for source_id in (first_id, second_id):
            root = owner_upload_root() / source_id
            if root.exists():
                for child in root.iterdir():
                    child.unlink()
                root.rmdir()
