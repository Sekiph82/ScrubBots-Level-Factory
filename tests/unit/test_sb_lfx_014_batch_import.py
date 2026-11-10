from __future__ import annotations

from pathlib import Path

from scrubbots_pixel_factory import owner_art_storage, owner_upload, studio_extensions
from scrubbots_pixel_factory.output.png import encode_logical_png
from scrubbots_pixel_factory.studio_extensions import batch_import


def test_batch_import_keeps_per_file_identity_and_truthful_partial_failure(tmp_path: Path, monkeypatch) -> None:
    # Isolated repository. The previous version imported into the owner's real
    # data/Level Factory/Imported and its cleanup deleted EVERY owner-upload-*
    # folder there (2026-11-10 incident); never touch the real checkout here.
    repository = tmp_path / "repository"
    imported_root = repository / "data" / "Level Factory" / "Imported"
    imported_root.mkdir(parents=True)
    monkeypatch.setattr(owner_art_storage, "factory_repository_root", lambda *_args, **_kwargs: repository)
    monkeypatch.setattr(owner_upload, "_repository_root", lambda *_args, **_kwargs: repository)
    monkeypatch.setattr(studio_extensions, "_repository_root", lambda *_args, **_kwargs: repository)
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda *_args, **_kwargs: imported_root)
    monkeypatch.setattr(studio_extensions, "owner_upload_root", lambda *_args, **_kwargs: imported_root)

    first = tmp_path / "same.png"; second_dir = tmp_path / "second"; second_dir.mkdir(); second = second_dir / "same.png"; corrupt = tmp_path / "bad.png"
    first.write_bytes(encode_logical_png(20, 20, ["C01", "C02", "C03", "C04"] * 100))
    second.write_bytes(encode_logical_png(20, 20, ["C05", "C06", "C07", "C08"] * 100))
    corrupt.write_bytes(b"not png")
    run = batch_import([first, second, first, corrupt])
    assert run["counts"]["success"] == 3
    assert run["counts"]["rejected"] == 1 and run["counts"]["failed"] == 0  # invalid PNG is a truthful REJECTED item
    ids = [item["source_id"] for item in run["items"][:3]]
    assert ids[0] != ids[1] and ids[0] == ids[2]
    assert run["items"][3]["source_id"] is None
    assert {path.name for path in imported_root.glob("owner-upload-*")} == {ids[0], ids[1]}
