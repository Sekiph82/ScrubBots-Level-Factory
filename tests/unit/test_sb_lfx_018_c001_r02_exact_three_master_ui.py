from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image
from scrubbots_pixel_factory import studio_extensions
from scrubbots_pixel_factory.supply_pipeline import release_pool


def test_owner_pages_projection_reads_validated_records_without_writing(tmp_path: Path, monkeypatch) -> None:
    extension_root = tmp_path / "studio-extensions"
    batches = extension_root / "batches"
    batches.mkdir(parents=True)
    batch_id = "batch-import-r01"
    batch = {
        "schema": studio_extensions.BATCH_SCHEMA,
        "version": 1,
        "batch_id": batch_id,
        "items": [{"index": 0, "display_path": "fixture.png", "source_id": "owner-upload-r01", "disposition": "IMPORTED"}],
        "counts": {"success": 1, "failed": 0},
        "created_at": "2026-10-08T00:00:00+00:00",
    }
    (batches / f"{batch_id}.json").write_text(json.dumps(batch), encoding="utf-8")
    before = {path.relative_to(tmp_path): path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}

    monkeypatch.setattr(studio_extensions, "extensions_root", lambda: extension_root)
    monkeypatch.setattr(studio_extensions, "candidate_inbox", lambda: {"candidates": [{"candidate_id": "candidate-r01"}]})
    monkeypatch.setattr(studio_extensions, "library_refresh", lambda: {"sources": [{"source_id": "owner-upload-r01"}]})
    monkeypatch.setattr(studio_extensions, "list_failures", lambda: {"failures": []})
    monkeypatch.setattr(release_pool, "release_entries", lambda: [{"candidate_id": "candidate-r01"}])

    projection = studio_extensions.owner_pages_snapshot()

    assert projection["read_only"] is True
    assert projection["mutated"] is False
    assert projection["batches"] == [batch]
    assert projection["candidates"] == [{"candidate_id": "candidate-r01"}]
    assert projection["sources"] == [{"source_id": "owner-upload-r01"}]
    assert projection["release_entries"] == [{"candidate_id": "candidate-r01"}]
    after = {path.relative_to(tmp_path): path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}
    assert after == before


def test_exact_three_master_ui_uses_owner_binary_and_canonical_actions() -> None:
    root = Path(__file__).resolve().parents[2]
    source = (root / "level_factory/scripts/factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    scene = (root / "level_factory/scenes/factory_studio.tscn").read_text(encoding="utf-8")
    binary = root / "docs/product/visual-masters/FACTORY_STUDIO_PIXEL_ART_MASTER_V04.png"
    runtime_binary = root / "level_factory/assets/visual-masters/FACTORY_STUDIO_PIXEL_ART_MASTER_V04.png"
    runtime_assets = root / "level_factory/assets/visual-masters"
    index = (root / "docs/product/visual-masters/FACTORY_STUDIO_VISUAL_MASTER_INDEX_V01.md").read_text(encoding="utf-8")

    assert '"PIXEL ART"' in source and '"LEVEL FACTORY"' in source and '"RELEASE POOL"' in source
    assert "FACTORY_STUDIO_PIXEL_ART_MASTER_V04.png" in scene
    assert "FACTORY_STUDIO_LEVEL_FACTORY_MASTER_V01.svg" in scene
    assert "FACTORY_STUDIO_RELEASE_POOL_MASTER_V01.svg" in scene
    for master_name in (
        "FACTORY_STUDIO_LEVEL_FACTORY_MASTER_V01.svg",
        "FACTORY_STUDIO_RELEASE_POOL_MASTER_V01.svg",
    ):
        assert (runtime_assets / master_name).read_bytes() == (root / "docs/product/visual-masters" / master_name).read_bytes()
        assert (runtime_assets / f"{master_name}.import").is_file()
    assert (runtime_assets / "FACTORY_STUDIO_PIXEL_ART_MASTER_V04.png.import").is_file()
    assert "owner-review" in source and '"pipeline"' in source
    assert '"release-pool"' in source and '"scrubbots-publish"' in source
    assert '"seed", "width", "height", "mode", "background_intent"' in source
    assert '_gateway.call("run_action", "Generate"' in source
    assert '"column_count": _column_count' in source and 'columns in [3, 4, 5]' in source
    assert 'str(_last_pipeline.get("disposition", "")) != "READY"' in source
    legacy_shell = scene.split('[node name="Frame"', 1)[1].split('[node name="Layout"', 1)[0]
    assert "visible = false" in legacy_shell
    assert "MasterUI" in scene
    assert "PIXEL_ART_FINAL.png" in (root / "level_factory/tests/factory_studio_owner_visual_evidence_suite.gd").read_text(encoding="utf-8")
    assert "FACTORY_STUDIO_PIXEL_ART_MASTER_V04.png" in index
    assert hashlib.sha256(binary.read_bytes()).hexdigest() == "b03f00cf01374a5cf884ce572637cbf06a654bb30a6262e28f4e0d76efd10def"
    assert runtime_binary.read_bytes() == binary.read_bytes()
    with Image.open(binary) as image:
        assert image.format == "PNG"
        assert image.size == (1536, 1024)
