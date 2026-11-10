"""Owner 2026-11-10: a PNG must keep its PixelLab Final name (LF-xxxxxx.png) everywhere.

Generation-time imports kept the staging name sprite-NN.png in Imported and in
Release Pool/Pending, so names differed between folders and Run Pending Batch was
rejected. The startup Final->Pending sync now aligns both to the Final name.
"""
import hashlib
import json
from io import BytesIO
from pathlib import Path

from PIL import Image

from scrubbots_pixel_factory import owner_folder_batch, owner_release_library, owner_upload, studio_extensions


def test_sync_renames_imported_and_pending_to_final_name(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path
    final = root / "data/output/Pixellab/Final"
    final.mkdir(parents=True)
    image = BytesIO()
    Image.new("RGBA", (32, 32), (20, 40, 60, 255)).save(image, format="PNG")
    raw = image.getvalue()
    staging = root / "staging" / "sprite-01.png"
    staging.parent.mkdir()
    staging.write_bytes(raw)
    (final / "LF-000305.png").write_bytes(raw)
    digest = hashlib.sha256(raw).hexdigest()
    source_id = "owner-upload-" + digest

    imported = owner_upload.import_owner_upload(staging, repository_root=root)   # staging name, as before the fix
    assert imported["original_filename"] == "sprite-01.png"
    owner_release_library.transition(
        source_id, "PENDING", source_sha256=digest, provider="PIXELLAB",
        original_source_path=str(root / "data/Level Factory/Imported" / source_id / "sprite-01.png"),
        reason="legacy staging-name Pending record", repository_root=root)
    assert (root / "data/Release Pool/Pending/sprite-01.png").is_file()

    monkeypatch.setattr(owner_folder_batch, "scan_owner_source_folder", lambda _folder, **_kwargs: {
        "provider": "PIXELLAB", "entries": [{"disposition": "ALREADY_IMPORTED", "source_sha256": digest,
                                             "path": str(final / "LF-000305.png"), "display_path": "LF-000305.png"}]})

    active, invalid, _verified = studio_extensions._sync_current_pixellab_final_sources(root)

    assert invalid == [] and active == {source_id}
    record_dir = root / "data/Level Factory/Imported" / source_id
    assert sorted(p.name for p in record_dir.iterdir()) == ["LF-000305.png", "source.json"]
    assert json.loads((record_dir / "source.json").read_text(encoding="utf-8"))["original_filename"] == "LF-000305.png"
    assert (record_dir / "LF-000305.png").read_bytes() == raw
    pending = root / "data/Release Pool/Pending"
    assert sorted(p.name for p in pending.glob("*.png")) == ["LF-000305.png"]
    history = sorted((root / "data/Release Pool/.history" / source_id).glob("*.json"))
    assert len(history) == 2                                  # append-only: original event kept
    current = owner_release_library.list_records(repository_root=root)["records"][0]
    assert current["status"] == "PENDING" and Path(current["original_source_path"]).name == "LF-000305.png"
    # Run Pending Batch accepts it (identity and names now agree).
    from scrubbots_pixel_factory import owner_art_storage

    monkeypatch.setattr(owner_art_storage, "factory_repository_root", lambda *_a, **_k: root)
    monkeypatch.setattr(studio_extensions, "_repository_root", lambda *_args, **_kwargs: root)
    assert studio_extensions.create_pending_png_batch([source_id])["pending_verified_count"] == 1
