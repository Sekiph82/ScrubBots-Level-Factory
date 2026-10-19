from __future__ import annotations

import json
from pathlib import Path

from scrubbots_pixel_factory import owner_upload, studio_extensions as studio
from scrubbots_pixel_factory.output.bundle import read_bundle
from scrubbots_pixel_factory.output.png import encode_logical_png


def test_legacy_verified_owner_bundle_gets_read_only_classification_projection(
    tmp_path: Path, monkeypatch
) -> None:
    repository = tmp_path / "repository"
    source_root = repository / "level_factory" / "output" / "owner-uploads"
    monkeypatch.setattr(owner_upload, "_repository_root", lambda: repository)
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda: source_root)
    monkeypatch.setattr(studio, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "owner_upload_root", lambda: source_root)
    monkeypatch.setattr(studio, "extensions_root", lambda: repository / "level_factory" / "output" / "studio-extensions")

    source = tmp_path / "owner.png"
    source.write_bytes(encode_logical_png(20, 20, ["C01", "C02", "C03", "C04"] * 100))
    imported = owner_upload.import_owner_upload(source)
    assert imported["state"] == "IMPORTED"
    validation = studio.validate_owner_source(str(imported["source_id"]))
    candidate_id, bundle_path = studio._derive_owner_candidate(
        str(imported["source_id"]), validation,
        studio._source_record_paths(str(imported["source_id"]))[1],
    )

    metadata_path = bundle_path / "metadata.json"
    stored_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    del stored_metadata["generator_metadata"]["classification"]
    metadata_path.write_text(json.dumps(stored_metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8")
    legacy_bytes = metadata_path.read_bytes()

    loaded = read_bundle(bundle_path)

    classification = loaded.metadata["generator_metadata"]["classification"]
    assert classification["candidate_class"] == "PRODUCTION_CANDIDATE"
    assert classification["candidate_id"] == candidate_id
    assert metadata_path.read_bytes() == legacy_bytes
