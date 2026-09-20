from __future__ import annotations

from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest, GeneratorRouter, export_candidate
from scrubbots_pixel_factory.studio_extensions import compare_candidates, record_owner_review


def test_comparison_is_identity_bound_and_read_only(tmp_path: Path) -> None:
    destination = Path("level_factory/output/.lfx-007-test")
    destination.mkdir(parents=True, exist_ok=True)
    paths = []
    ids = ["lfx007-left", "lfx007-right"]
    for seed, candidate_id in zip((301, 302), ids, strict=True):
        candidate = GeneratorRouter().generate_candidate(GenerationRequest("EASY", seed, "MASK", width=20, height=20))
        paths.append(export_candidate(candidate, candidate_id, destination))
    before = [{item.name: item.read_bytes() for item in path.iterdir()} for path in paths]
    try:
        record_owner_review(ids[0], "ACCEPT", "left only")
        view = compare_candidates(ids)
        assert view["read_only"] is True
        assert view["winner"]["disposition"] == "NOT AVAILABLE"
        assert [item["candidate_id"] for item in view["candidates"]] == ids
        assert view["candidates"][0]["owner_review"]["disposition"] == "ACCEPT"
        assert view["candidates"][1]["owner_review"]["disposition"] == "NOT AVAILABLE"
        assert all({item.name: item.read_bytes() for item in path.iterdir()} == snapshot for path, snapshot in zip(paths, before, strict=True))
    finally:
        for path in paths:
            for item in path.iterdir(): item.unlink()
            path.rmdir()
        destination.rmdir()
        for path in Path("level_factory/output/studio-extensions/owner-review").glob("review-lfx007-*.json"):
            path.unlink()
