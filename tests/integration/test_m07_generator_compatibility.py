import json
from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest, GeneratorOptions
from scrubbots_pixel_factory.generators.mask import MaskSpriteGenerator
from scrubbots_pixel_factory.generators.rules import RuleShapeGenerator
from scrubbots_pixel_factory.generators.router import HybridGenerator, GeneratorRouter
from scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCGenerator
from scrubbots_pixel_factory.quality import QualityPolicy, evaluate_grid


ROOT = Path(__file__).parents[2]


def test_m03_m04_m05_m06_results_can_be_analyzed_without_private_topology() -> None:
    conservative = QualityPolicy(max_isolated_ratio=0.35, max_tiny_cell_ratio=0.60, max_color_dominance_ratio=1.0)
    results = [
        MaskSpriteGenerator().generate(GenerationRequest("EASY", 11, "MASK", width=20, height=20, style="ROBOT")),
        RuleShapeGenerator().generate(GenerationRequest("EASY", 23, "RULES", width=20, height=20, style="ORGANIC")),
        HybridGenerator().generate(GenerationRequest(
            "EASY", 47, "HYBRID", width=20, height=20,
            generator_options=GeneratorOptions("hybrid", 1, {
                "strategy": "MASK_GEOMETRY_RULE_COLOR_REGIONS",
                "mask_style": "ROBOT", "rules_style": "ORGANIC", "mask_symmetry": "HORIZONTAL",
            }),
        )),
    ]
    for result in results:
        assert result.is_success
        report = evaluate_grid(result.width, result.height, result.logical_grid, policy=conservative)
        assert report.analysis is not None
        assert report.accepted is True
        assert report.analysis.width == result.width
        assert report.analysis.height == result.height


def test_m05_wfc_and_m06_auto_results_are_compatible_with_grid_only_quality() -> None:
    raw = json.loads((ROOT / "tests" / "fixtures" / "wfc" / "wfc-synthetic-easy-3.json").read_text(encoding="utf-8"))
    exemplar = Exemplar(
        raw["schema"], raw["version"], raw["exemplar_id"], raw["role"], raw["width"], raw["height"],
        tuple(raw["pixels"]), raw["provenance_type"], raw["provenance_description"], raw["ownership"],
    )
    wfc_request = GenerationRequest(
        "EASY", 11, "WFC", width=20, height=20, style=exemplar.exemplar_id,
        palette_subset=exemplar.source_palette,
        generator_options=GeneratorOptions("wfc", 1, {"pattern_size": 2, "input_periodic": True}),
    )
    wfc_result = WFCGenerator(ExemplarRegistry((exemplar,))).generate(wfc_request)
    assert wfc_result.is_success
    wfc_quality_policy = QualityPolicy(max_isolated_ratio=1.0, max_tiny_cell_ratio=1.0, max_color_dominance_ratio=1.0)
    wfc_report = evaluate_grid(wfc_result.width, wfc_result.height, wfc_result.logical_grid, policy=wfc_quality_policy)
    assert wfc_report.analysis is not None
    assert wfc_report.accepted is True

    auto_request = GenerationRequest(
        "EASY", 17, "AUTO", width=20, height=20,
        generator_options=GeneratorOptions("auto", 1, {"candidates": ["MASK", "RULES"], "fallback_on_failure": True}),
    )
    auto_result = GeneratorRouter().generate(auto_request)
    assert auto_result.is_success
    auto_report = evaluate_grid(auto_result.width, auto_result.height, auto_result.logical_grid, policy=QualityPolicy(max_isolated_ratio=0.35, max_tiny_cell_ratio=0.60, max_color_dominance_ratio=1.0))
    assert auto_report.analysis is not None
    assert auto_report.accepted is True
