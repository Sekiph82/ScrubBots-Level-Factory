import json
from pathlib import Path

import pytest

from scrubbots_pixel_factory import GenerationRequest, GeneratorRouter, QualityPolicy, evaluate_grid, logical_grid_hash, select_palette_subset
from scrubbots_pixel_factory.core.request import RequestContractError
from scrubbots_pixel_factory.contracts.difficulty import dimension_band
from tools.m10_prepare import DIFFICULTIES, build_property_corpus, _request


CORPUS_PATH = Path("review/m10/M10_PROPERTY_CORPUS.json")


def test_m10_corpus_is_versioned_and_has_required_valid_cases() -> None:
    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    assert corpus["schema"] == "scrubbots-m10-property-corpus"
    assert corpus["corpus_version"] == "m10-property-corpus-v1"
    assert corpus["case_count"] >= 2000
    assert len(corpus["cases"]) == corpus["case_count"]
    assert {case["request"]["difficulty"] for case in corpus["cases"]} == set(DIFFICULTIES)
    assert {case["request"]["generator_mode"] for case in corpus["cases"]} >= {"MASK", "RULES", "HYBRID", "AUTO", "WFC"}
    assert len({case["request_digest"] for case in corpus["cases"]}) == corpus["case_count"]
    assert len(corpus["invalid_cases"]) >= 5


@pytest.mark.parametrize("difficulty", DIFFICULTIES)
@pytest.mark.parametrize("mode", ("MASK", "RULES", "HYBRID", "AUTO"))
def test_m10_successful_samples_preserve_logical_contracts(difficulty: str, mode: str) -> None:
    palette = select_palette_subset(difficulty, f"m10-property-sample-{difficulty}-{mode}")
    request = _request(difficulty, f"m10-property-sample-{difficulty}-{mode}", mode, 1, dimensions=(dimension_band(difficulty).minimum, dimension_band(difficulty).minimum + 1), palette=palette)
    first = GeneratorRouter().generate_candidate(request)
    second = GeneratorRouter().generate_candidate(request)
    result = first.result if hasattr(first, "result") else first
    repeat = second.result if hasattr(second, "result") else second
    assert result.is_success, result.failure_reason
    assert result.canonical_bytes() == repeat.canonical_bytes()
    assert result.width * result.height == len(result.logical_grid)
    assert tuple(result.used_palette) == tuple(sorted(result.used_palette, key=lambda value: int(value[1:])))
    assert "BG01" not in result.logical_grid
    assert logical_grid_hash(result.width, result.height, result.logical_grid)
    assert evaluate_grid(result.width, result.height, result.logical_grid, policy=QualityPolicy(difficulty=difficulty)).analysis is not None


def test_m10_corpus_builder_is_repeatable() -> None:
    first = build_property_corpus()
    second = build_property_corpus()
    assert json.dumps(first, sort_keys=True, separators=(",", ":")) == json.dumps(second, sort_keys=True, separators=(",", ":"))


def test_m10_invalid_request_corpus_fails_closed() -> None:
    with pytest.raises(RequestContractError):
        GenerationRequest("IMPOSSIBLE", "bad", "MASK", width=20, height=20)
    with pytest.raises(RequestContractError):
        GenerationRequest("EASY", "bad", "NOPE", width=20, height=20)
    with pytest.raises(RequestContractError):
        GenerationRequest("EASY", True, "MASK", width=20, height=20)
