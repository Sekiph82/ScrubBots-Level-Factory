from __future__ import annotations

from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest, GeneratorRouter, export_candidate
from scrubbots_pixel_factory.studio_extensions import candidate_inbox, extensions_root, record_owner_review


def test_candidate_inbox_uses_real_bundle_and_review_history_is_append_only(tmp_path: Path) -> None:
    destination = Path("level_factory/output/.lfx-006-test/candidates")
    destination.mkdir(parents=True, exist_ok=True)
    candidate = GeneratorRouter().generate_candidate(GenerationRequest("EASY", 123, "MASK", width=20, height=20))
    candidate_id = "lfx006-review-candidate"
    path = export_candidate(candidate, candidate_id, destination)
    before = {item.name: item.read_bytes() for item in path.iterdir()}
    try:
        inbox = candidate_inbox()
        assert any(item["candidate_id"] == candidate_id for item in inbox["candidates"])
        accepted = record_owner_review(candidate_id, "ACCEPT", "owner accepted", "keep")
        rejected = record_owner_review(candidate_id, "REJECT", "second review", "revisit")
        assert rejected["previous_review_id"] == accepted["review_id"]
        assert len(list((extensions_root() / "owner-review").glob(f"review-{candidate_id}-*.json"))) == 2
        after = {item.name: item.read_bytes() for item in path.iterdir()}
        assert after == before
    finally:
        if path.exists():
            for item in path.iterdir(): item.unlink()
            path.rmdir()
        if destination.exists(): destination.rmdir()
        if destination.parent.exists(): destination.parent.rmdir()
        for item in (extensions_root() / "owner-review").glob(f"review-{candidate_id}-*.json"):
            item.unlink()
