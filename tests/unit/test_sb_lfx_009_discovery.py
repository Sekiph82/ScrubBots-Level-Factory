from __future__ import annotations

from pathlib import Path

from scrubbots_pixel_factory.owner_upload import import_owner_upload, owner_upload_root
from scrubbots_pixel_factory.output.png import encode_logical_png
from scrubbots_pixel_factory.studio_extensions import discover_records, save_library_metadata


def test_discovery_is_fresh_deterministic_and_unavailable_collections_do_not_guess(isolated_studio_repository: Path, tmp_path: Path) -> None:
    # Imported Sources lists only sources whose PNG is currently in PixelLab Final.
    from scrubbots_pixel_factory.owner_art_storage import owner_art_paths

    path = owner_art_paths(isolated_studio_repository)["pixellab_final"] / "discover.png"
    path.parent.mkdir(parents=True)
    path.write_bytes(encode_logical_png(56, 56, ["C01", "C02", "C03", "C04"] * 784))  # Final accepts 51..59 px
    imported = import_owner_upload(path)
    source_id = str(imported["source_id"])
    assert (owner_upload_root() / source_id).is_dir()
    save_library_metadata(source_id, "Searchable Source", ["needs-review"])
    view = discover_records("searchable", collection="Imported Sources")
    assert view["state"] == "READY"
    assert [record["record_id"] for record in view["records"]] == [source_id]
    assert view["mutated"] is False
    unavailable = discover_records(collection="Ready for Production")
    assert unavailable["state"] == "NOT AVAILABLE"
    assert unavailable["records"] == []

