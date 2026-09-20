from __future__ import annotations

from pathlib import Path

from scrubbots_pixel_factory.output.png import encode_logical_png
from scrubbots_pixel_factory.owner_upload import owner_upload_root
from scrubbots_pixel_factory.studio_extensions import batch_import, extensions_root


def test_batch_import_keeps_per_file_identity_and_truthful_partial_failure(tmp_path: Path) -> None:
    first = tmp_path / "same.png"; second_dir = tmp_path / "second"; second_dir.mkdir(); second = second_dir / "same.png"; corrupt = tmp_path / "bad.png"
    first.write_bytes(encode_logical_png(20, 20, ["C01", "C02", "C03", "C04"] * 100))
    second.write_bytes(encode_logical_png(20, 20, ["C05", "C06", "C07", "C08"] * 100))
    corrupt.write_bytes(b"not png")
    run = batch_import([first, second, first, corrupt])
    try:
        assert run["counts"]["success"] == 3
        assert run["counts"]["failed"] == 1
        ids = [item["source_id"] for item in run["items"][:3]]
        assert ids[0] != ids[1] and ids[0] == ids[2]
        assert run["items"][3]["source_id"] is None
    finally:
        for source_dir in owner_upload_root().glob("owner-upload-*"):
            if source_dir.is_dir():
                for child in source_dir.iterdir(): child.unlink()
                source_dir.rmdir()
        path = extensions_root() / "batches" / f"{run['batch_id']}.json"
        if path.exists(): path.unlink()
