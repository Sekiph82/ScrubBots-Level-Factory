"""Inventory must not rescan every Release Pool projection per new Final source (2026-11-16)."""
import json
from pathlib import Path

import pytest

from scrubbots_pixel_factory import owner_release_library as lib


def _write(tmp_path: Path, name: str) -> Path:
    from PIL import Image
    p = tmp_path / name
    Image.new("RGBA", (56, 56), (10, 20, 30, 255)).save(p)
    return p


def test_list_records_source_filter_returns_only_that_source(tmp_path):
    rows = []
    for i in range(3):
        p = _write(tmp_path, f"LF-{i:06d}.png")
        from PIL import Image
        im = Image.open(p); im.putpixel((i, i), (200, 0, 0, 255)); im.save(p)
        import hashlib
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        lib.transition("owner-upload-" + sha, "PENDING", source_sha256=sha, provider="PIXELLAB",
                       original_source_path=str(p), repository_root=tmp_path)
        rows.append("owner-upload-" + sha)
    assert len(lib.list_records(repository_root=tmp_path)["records"]) == 3
    one = lib.list_records(source_id=rows[1], repository_root=tmp_path)["records"]
    assert [r["source_id"] for r in one] == [rows[1]]
    assert lib.list_records(source_id="owner-upload-" + "0" * 64, repository_root=tmp_path)["records"] == []
    with pytest.raises(lib.OwnerReleaseLibraryError):
        lib.list_records(source_id="../x", repository_root=tmp_path)


def test_inventory_uses_single_source_lookup():
    src = Path("src/scrubbots_pixel_factory/studio_extensions.py").read_text(encoding="utf-8")
    assert "latest = list_owner_release_records(source_id=source_id," in src
