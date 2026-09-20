from __future__ import annotations

from pathlib import Path

from scrubbots_pixel_factory.owner_upload import import_owner_upload, owner_upload_root
from scrubbots_pixel_factory.output.png import encode_logical_png
from scrubbots_pixel_factory.studio_extensions import discover_records, save_library_metadata


def test_discovery_is_fresh_deterministic_and_unavailable_collections_do_not_guess(tmp_path: Path) -> None:
    path = tmp_path / "discover.png"
    path.write_bytes(encode_logical_png(20, 20, ["C01", "C02", "C03", "C04"] * 100))
    imported = import_owner_upload(path)
    source_id = str(imported["source_id"])
    try:
        save_library_metadata(source_id, "Searchable Source", ["needs-review"])
        view = discover_records("searchable", collection="Imported Sources")
        assert view["state"] == "READY"
        assert [record["record_id"] for record in view["records"]] == [source_id]
        assert view["mutated"] is False
        unavailable = discover_records(collection="Ready for Production")
        assert unavailable["state"] == "NOT AVAILABLE"
        assert unavailable["records"] == []
    finally:
        root = owner_upload_root() / source_id
        for child in root.iterdir(): child.unlink()
        root.rmdir()
        metadata = Path("level_factory/output/studio-extensions/source-library/metadata") / f"{source_id}.json"
        if metadata.exists(): metadata.unlink()
