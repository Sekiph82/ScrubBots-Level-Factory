from __future__ import annotations

import json
from pathlib import Path

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


def test_owner_page_routes_and_authority_calls_remain_explicit() -> None:
    source = (Path(__file__).resolve().parents[2] / "level_factory/scripts/factory_studio_workspace_page.gd").read_text(encoding="utf-8")

    assert '"HOME"' in source and '"CREATE"' in source and '"BATCH"' in source
    assert '"SOLVE"' in source and '"REVIEW"' in source and '"LIBRARY"' in source
    assert '"PUBLISH"' in source and '"SETTINGS"' in source
    assert '"owner-review"' in source
    assert '"pipeline"' in source
    assert '"retry-failure"' in source
    assert '"discover"' in source
    assert '"VISUAL FIXTURE — not canonical data' in source
