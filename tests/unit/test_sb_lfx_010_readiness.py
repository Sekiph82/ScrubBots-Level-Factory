from __future__ import annotations

from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest, GeneratorRouter, export_candidate
from scrubbots_pixel_factory.studio_extensions import readiness_card


def test_readiness_card_exposes_all_gates_and_never_falsely_returns_ready() -> None:
    destination = Path("level_factory/output/.lfx-010-test")
    destination.mkdir(parents=True, exist_ok=True)
    candidate = GeneratorRouter().generate_candidate(GenerationRequest("EASY", 123, "MASK", width=20, height=20))
    path = export_candidate(candidate, "lfx010-ready", destination)
    try:
        card = readiness_card("lfx010-ready")
        assert set(card["gates"]) == {"SOURCE", "PALETTE", "STRUCTURE", "SOLVER", "DIFFICULTY", "QA", "OWNER", "EXPORT"}
        assert card["gates"]["SOLVER"]["disposition"] == "NOT_AVAILABLE"
        assert card["gates"]["DIFFICULTY"]["disposition"] == "NOT_AVAILABLE"
        assert card["overall"] == "NOT READY"
    finally:
        for child in path.iterdir(): child.unlink()
        path.rmdir()
        destination.rmdir()
