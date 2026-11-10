"""P0-A follow-up: generation-time imports of two atlases both carried the staging
name sprite-01.png; Release Pool names status artwork by the source basename, so
the second atlas could never enter Pending ("readable status artwork name conflicts
with different source bytes"). The Final→Pending sync now names it from Final."""
import hashlib
import json
from io import BytesIO
from pathlib import Path

from PIL import Image

from scrubbots_pixel_factory import owner_folder_batch, owner_release_library, owner_upload, studio_extensions


def _png(color) -> bytes:
    image = BytesIO()
    Image.new("RGBA", (32, 32), color).save(image, format="PNG")
    return image.getvalue()


def test_two_atlases_with_same_staging_name_both_enter_pending(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path
    final = root / "data/output/Pixellab/Final"
    final.mkdir(parents=True)
    (root / "data/Release Pool").mkdir(parents=True)
    imported_root = root / "data/Level Factory/Imported"
    sources = {}
    for name, color in (("LF-000401.png", (20, 40, 60, 255)), ("LF-000417.png", (60, 40, 20, 255))):
        raw = _png(color)
        (final / name).write_bytes(raw)
        digest = hashlib.sha256(raw).hexdigest()
        source_id = "owner-upload-" + digest
        staged = imported_root / source_id / "sprite-01.png"   # per-atlas staging name
        staged.parent.mkdir(parents=True)
        staged.write_bytes(raw)
        # Real Imported records carry source.json; name alignment rewrites it.
        (staged.parent / "source.json").write_bytes(owner_upload._canonical_json_bytes(
            owner_upload._record(source_id, digest, len(raw), "sprite-01.png", 32, 32)))
        sources[source_id] = {"digest": digest, "final": final / name, "imported": staged}

    monkeypatch.setattr(owner_folder_batch, "scan_owner_source_folder", lambda _folder, **_kwargs: {
        "provider": "PIXELLAB", "entries": [
            {"disposition": "ALREADY_IMPORTED", "source_sha256": s["digest"], "path": str(s["final"]),
             "display_path": s["final"].name} for s in sources.values()]})
    monkeypatch.setattr(studio_extensions, "owner_upload_root", lambda _root=None: imported_root)
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda _root=None: imported_root)

    def verify(source_id, **_kwargs):
        record = json.loads((imported_root / source_id / "source.json").read_text(encoding="utf-8"))
        return {"source_id": source_id, "source_sha256": sources[source_id]["digest"],
                "source_path": str(imported_root / source_id / record["original_filename"]),
                "original_filename": record["original_filename"]}

    monkeypatch.setattr(studio_extensions, "verify_owner_source", verify)

    active, invalid, _verified = studio_extensions._sync_current_pixellab_final_sources(root)

    assert invalid == [], invalid
    assert active == set(sources)
    pending = root / "data/Release Pool/Pending"
    assert sorted(p.name for p in pending.glob("*.png")) == ["LF-000401.png", "LF-000417.png"]
    records = owner_release_library.list_records(repository_root=root)["records"]
    assert {Path(r["original_source_path"]).name for r in records} == {"LF-000401.png", "LF-000417.png"}
