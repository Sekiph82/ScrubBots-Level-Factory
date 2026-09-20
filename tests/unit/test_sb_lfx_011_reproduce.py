from __future__ import annotations

from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest, GeneratorRouter, export_candidate
from scrubbots_pixel_factory.studio_extensions import reproduce_capability


def test_reproduce_capability_distinguishes_deterministic_candidate() -> None:
    destination = Path("level_factory/output/.lfx-011-test")
    destination.mkdir(parents=True, exist_ok=True)
    candidate = GeneratorRouter().generate_candidate(GenerationRequest("EASY", 123, "MASK", width=20, height=20))
    path = export_candidate(candidate, "lfx011-repro", destination)
    try:
        capability = reproduce_capability("lfx011-repro")
        assert capability["disposition"] == "EXACT_REPRODUCIBLE"
        assert "recorded" in capability["reason"]
    finally:
        for child in path.iterdir(): child.unlink()
        path.rmdir(); destination.rmdir()
