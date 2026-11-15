"""Owner 2026-11-15: rejected art is deleted, not kept; purging must survive reconciliation
and must not invalidate the other slices of a partly purged atlas."""
from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from scrubbots_pixel_factory import owner_release_library as library


def _png(color: tuple[int, int, int]) -> bytes:
    buffer = BytesIO()
    Image.new("RGBA", (56, 56), (*color, 255)).save(buffer, format="PNG")
    return buffer.getvalue()


def test_purged_rejected_source_is_not_rebuilt(tmp_path: Path) -> None:
    import hashlib

    raw = _png((10, 20, 30))
    sha = hashlib.sha256(raw).hexdigest()
    source = tmp_path / "LF-000001.png"
    source.write_bytes(raw)
    source_id = f"owner-upload-{sha}"
    library.transition(source_id, "REJECTED", source_sha256=sha, provider="PIXELLAB",
                       original_source_path=str(source), reason="test", repository_root=tmp_path)
    assert library.list_records(repository_root=tmp_path)["counts"]["REJECTED"] == 1

    deleted = library.purge_rejected_source(source_id, repository_root=tmp_path)

    assert deleted
    library.reconcile_status_projections(repository_root=tmp_path)
    assert library.list_records(repository_root=tmp_path)["records"] == []


def test_only_rejected_sources_can_be_purged(tmp_path: Path) -> None:
    import hashlib

    raw = _png((40, 50, 60))
    sha = hashlib.sha256(raw).hexdigest()
    source = tmp_path / "LF-000002.png"
    source.write_bytes(raw)
    library.transition(f"owner-upload-{sha}", "PENDING", source_sha256=sha, provider="PIXELLAB",
                       original_source_path=str(source), reason="test", repository_root=tmp_path)
    with pytest.raises(library.OwnerReleaseLibraryError):
        library.purge_rejected_source(f"owner-upload-{sha}", repository_root=tmp_path)


def test_partly_purged_atlas_keeps_its_other_slices_valid(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import hashlib

    from scrubbots_pixel_factory import owner_art_storage, owner_folder_batch

    monkeypatch.setattr(owner_art_storage, "factory_repository_root", lambda anchor=None: tmp_path)
    paths = owner_art_storage.ensure_owner_art_layout(tmp_path)
    slices, atlas = [], Image.new("RGBA", (224, 224), (0, 0, 0, 0))
    for index in range(1, 17):
        raw = _png((index * 10, 5, 5))
        name = f"LF-{index:06d}.png"
        (paths["pixellab_final"] / name).write_bytes(raw)
        atlas.paste(Image.open(BytesIO(raw)), (((index - 1) % 4) * 56, ((index - 1) // 4) * 56))
        slices.append({"index": index, "sha256": hashlib.sha256(raw).hexdigest(), "filename": name})
    buffer = BytesIO()
    atlas.save(buffer, format="PNG")
    atlas_sha = hashlib.sha256(buffer.getvalue()).hexdigest()
    (paths["pixellab_grid_files"] / "PX-ATLAS-000001.png").write_bytes(buffer.getvalue())
    transaction = {"schema": "scrubbots-pixellab-atlas-transaction/v1", "source_atlas_sha256": atlas_sha, "state": "FINALIZED",
                   "frame_dimensions": [56, 56], "atlas_dimensions": [224, 224], "atlas_filename": "PX-ATLAS-000001.png",
                   "source_kind": "IMPORTED_ATLAS", "slices": slices}
    (paths["pixellab_transactions"] / f"pixellab-atlas-{atlas_sha}.json").write_text(json.dumps(transaction), encoding="utf-8")

    owner_art_storage.purge_final_slice("LF-000003.png", slices[2]["sha256"])

    index = owner_folder_batch._pixellab_transaction_index(paths)
    assert "LF-000003.png" not in index and not (paths["pixellab_final"] / "LF-000003.png").exists()
    assert all(index[f"LF-{i:06d}.png"]["group_valid"] == "true" for i in range(1, 17) if i != 3)
