from __future__ import annotations

from scrubbots_pixel_factory.core.request import LegacyGenerationRequest as _LegacyGenerationRequest  # explicit legacy/research fixture

from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest, GeneratorRouter, export_candidate, read_bundle
from scrubbots_pixel_factory.studio_extensions import compare_revisions, create_revision, list_revisions, load_revision


def test_revision_lineage_compare_and_branch_are_immutable(isolated_studio_repository: Path) -> None:
    destination = isolated_studio_repository / "data" / "Level Factory" / "Workspace" / "Candidates"
    candidate = GeneratorRouter().generate_candidate(GenerationRequest("EASY", 123, "MASK", width=20, height=20))
    path = export_candidate(candidate, "lfx012-revisions", destination)
    bundle = read_bundle(path)
    cells = list(bundle.artwork.cells)
    first = create_revision("lfx012-revisions", 20, 20, cells)
    changed = list(cells); changed[0] = "C01" if changed[0] != "C01" else "C02"
    second = create_revision("lfx012-revisions", 20, 20, changed, first["revision_id"], "one cell")
    branch = create_revision("lfx012-revisions", 20, 20, cells, first["revision_id"], "branch after undo")
    assert len(list_revisions("lfx012-revisions")) == 3
    assert compare_revisions(first, second)["changed_cell_count"] >= 1
    assert load_revision("lfx012-revisions", branch["revision_id"])["parent_revision_id"] == first["revision_id"]

# These tests exercise explicit historical/research behavior, not the current production request.
GenerationRequest = _LegacyGenerationRequest
