from __future__ import annotations

from scrubbots_pixel_factory.core.request import LegacyGenerationRequest as _LegacyGenerationRequest  # explicit legacy/research fixture

from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest, GeneratorRouter, export_candidate
from scrubbots_pixel_factory.studio_extensions import readiness_card


def test_readiness_card_exposes_all_gates_and_never_falsely_returns_ready(isolated_studio_repository: Path) -> None:
    destination = isolated_studio_repository / "data" / "Level Factory" / "Workspace" / "Candidates"
    candidate = GeneratorRouter().generate_candidate(GenerationRequest("EASY", 123, "MASK", width=20, height=20))
    export_candidate(candidate, "lfx010-ready", destination)
    card = readiness_card("lfx010-ready")
    assert set(card["gates"]) == {"SOURCE", "PALETTE", "STRUCTURE", "SOLVER", "DIFFICULTY", "QA", "LOAD_CHECK", "OWNER", "EXPORT"}
    assert card["gates"]["SOLVER"]["disposition"] == "NOT_AVAILABLE"
    assert card["gates"]["DIFFICULTY"]["disposition"] == "NOT_AVAILABLE"
    assert card["overall"] == "NOT READY"

# These tests exercise explicit historical/research behavior, not the current production request.
GenerationRequest = _LegacyGenerationRequest
