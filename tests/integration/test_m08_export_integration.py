from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

import pytest

from scrubbots_pixel_factory import GenerationRequest, GeneratorOptions
from scrubbots_pixel_factory.generators.mask import MaskSpriteGenerator
from scrubbots_pixel_factory.generators.rules import RuleShapeGenerator
from scrubbots_pixel_factory.generators.router import GeneratorRouter, HybridGenerator
from scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCGenerator
from scrubbots_pixel_factory.output import (
    BundleConflictError,
    OutputContractError,
    build_export_bundle,
    export_result,
    read_bundle,
    write_bundle,
)
from scrubbots_pixel_factory.quality import QualityPolicy, evaluate_grid


ROOT = Path(__file__).parents[2]


def _mask_result(seed: int = 11, width: int = 20, height: int = 20):
    return MaskSpriteGenerator().generate(GenerationRequest("EASY", seed, "MASK", width=width, height=height, style="ROBOT"))


def _wfc_candidate():
    raw = json.loads((ROOT / "tests" / "fixtures" / "wfc" / "wfc-synthetic-easy-3.json").read_text(encoding="utf-8"))
    exemplar = Exemplar(raw["schema"], raw["version"], raw["exemplar_id"], raw["role"], raw["width"], raw["height"], tuple(raw["pixels"]), raw["provenance_type"], raw["provenance_description"], raw["ownership"])
    request = GenerationRequest("EASY", 11, "WFC", width=20, height=20, style=exemplar.exemplar_id, palette_subset=exemplar.source_palette, generator_options=GeneratorOptions("wfc", 1, {"pattern_size": 2, "input_periodic": True}))
    return WFCGenerator(ExemplarRegistry((exemplar,))).generate_candidate(request)


def test_m08_representative_mask_rules_hybrid_auto_and_wfc_provenance() -> None:
    mask = _mask_result()
    rules = RuleShapeGenerator().generate(GenerationRequest("EASY", 23, "RULES", width=20, height=20, style="ORGANIC"))
    hybrid = HybridGenerator().generate_candidate(GenerationRequest("EASY", 47, "HYBRID", width=20, height=20, generator_options=GeneratorOptions("hybrid", 1, {"strategy": "MASK_GEOMETRY_RULE_COLOR_REGIONS", "mask_style": "ROBOT", "rules_style": "ORGANIC", "mask_symmetry": "HORIZONTAL"})))
    auto = GeneratorRouter().generate_candidate(GenerationRequest("EASY", 17, "AUTO", width=20, height=20, generator_options=GeneratorOptions("auto", 1, {"candidates": ["MASK", "RULES"], "fallback_on_failure": True})))
    assert mask.is_success and rules.is_success and hybrid.result.is_success and auto.result.is_success
    for candidate, name in ((mask, "mask"), (rules, "rules"), (hybrid, "hybrid"), (auto, "auto"), (_wfc_candidate(), "wfc")):
        bundle = build_export_bundle(candidate, f"representative-{name}")
        result = candidate.result if hasattr(candidate, "result") else candidate
        assert bundle.artwork.cells == tuple(result.logical_grid)
        assert bundle.metadata["generation"]["result_digest"] == result.digest()
        assert bundle.metadata["quality"]["grid_hash"] == bundle.artwork.grid_hash
    wfc_bundle = build_export_bundle(_wfc_candidate(), "representative-wfc")
    assert wfc_bundle.metadata["generator_metadata"]["payload"]["namespace"] == "wfc"
    assert wfc_bundle.metadata["generator_metadata"]["payload"]["data"]["exemplar_id"] == "wfc-synthetic-easy-3"


def test_m08_rich_raw_results_require_explicit_authoritative_metadata() -> None:
    wfc = _wfc_candidate()
    hybrid = HybridGenerator().generate_candidate(GenerationRequest("EASY", 47, "HYBRID", width=20, height=20, generator_options=GeneratorOptions("hybrid", 1, {"strategy": "MASK_GEOMETRY_RULE_COLOR_REGIONS", "mask_style": "ROBOT", "rules_style": "ORGANIC", "mask_symmetry": "HORIZONTAL"})))
    auto = GeneratorRouter().generate_candidate(GenerationRequest("EASY", 17, "AUTO", width=20, height=20, generator_options=GeneratorOptions("auto", 1, {"candidates": ["MASK", "RULES"], "fallback_on_failure": True})))
    assert hasattr(wfc, "result") and hasattr(hybrid, "result") and hasattr(auto, "result")
    for candidate in (wfc, hybrid, auto):
        with pytest.raises(OutputContractError):
            build_export_bundle(candidate.result, "raw-rich")
    with TemporaryDirectory() as temp:
        for name, candidate in (("wfc", wfc), ("hybrid", hybrid), ("auto", auto)):
            read_bundle(write_bundle(build_export_bundle(candidate, f"rich-{name}"), temp))
    for name, candidate, metadata in (("wfc", wfc, wfc.wfc_metadata), ("hybrid", hybrid, hybrid.hybrid_metadata), ("auto", auto, auto.auto_metadata)):
        wrapper = build_export_bundle(candidate, f"explicit-{name}")
        explicit = build_export_bundle(candidate.result, f"explicit-{name}", generator_metadata=metadata)
        assert wrapper.files == explicit.files
    with pytest.raises(OutputContractError):
        build_export_bundle(wfc.result, "wrong-namespace", generator_metadata={"namespace": "auto", "data": dict(wfc.wfc_metadata)})


def test_m08_rich_provenance_tampering_fails_on_bundle_read() -> None:
    wfc = _wfc_candidate()
    hybrid = HybridGenerator().generate_candidate(GenerationRequest("EASY", 47, "HYBRID", width=20, height=20, generator_options=GeneratorOptions("hybrid", 1, {"strategy": "MASK_GEOMETRY_RULE_COLOR_REGIONS", "mask_style": "ROBOT", "rules_style": "ORGANIC", "mask_symmetry": "HORIZONTAL"})))
    auto = GeneratorRouter().generate_candidate(GenerationRequest("EASY", 17, "AUTO", width=20, height=20, generator_options=GeneratorOptions("auto", 1, {"candidates": ["MASK", "RULES"], "fallback_on_failure": True})))
    cases = ((wfc, "exemplar_id", "unrelated-exemplar"), (hybrid, "final_result_digest", "0" * 64), (auto, "selected_engine_id", "tampered-engine"))
    for candidate, field, replacement in cases:
        with TemporaryDirectory() as temp:
            path = write_bundle(build_export_bundle(candidate, f"tamper-{field}"), temp)
            metadata_path = path / "metadata.json"
            value = json.loads(metadata_path.read_text(encoding="utf-8"))
            value["generator_metadata"]["payload"]["data"][field] = replacement
            metadata_path.write_text(json.dumps(value), encoding="utf-8")
            with pytest.raises(OutputContractError):
                read_bundle(path)


def test_m08_bundle_round_trip_rectangular_preview_and_rewrite() -> None:
    result = MaskSpriteGenerator().generate(GenerationRequest("EASY", 31, "MASK", width=20, height=27, style="ROBOT"))
    assert result.is_success
    with TemporaryDirectory() as temp:
        path = export_result(result, "rectangular", temp, preview_scale=2)
        first = read_bundle(path)
        second = build_export_bundle(result, "rectangular", preview_scale=2)
        assert first.files == second.files
        assert first.artwork.width == 20 and first.artwork.height == 27
        assert write_bundle(second, temp) == path
        assert sorted(item.name for item in path.iterdir()) == ["artwork.json", "artwork.png", "artwork.preview.png", "metadata.json"]


def test_m08_quality_reject_is_metadata_state_not_artwork_mutation() -> None:
    result = _mask_result()
    rejected = evaluate_grid(result.width, result.height, result.logical_grid, policy=QualityPolicy(max_largest_region_ratio=0.0))
    assert rejected.accepted is False
    bundle = build_export_bundle(result, "quality-rejected", quality_report=rejected)
    assert bundle.artwork.cells == result.logical_grid
    assert bundle.metadata["quality"]["decision"] == "REJECT"
    assert bundle.metadata["quality"]["rejection_codes"]


def test_m08_negative_cross_file_quality_png_hash_and_conflict_checks() -> None:
    result = _mask_result()
    with TemporaryDirectory() as temp:
        path = export_result(result, "corruption", temp)
        metadata_path = path / "metadata.json"
        original = metadata_path.read_bytes()
        value = json.loads(original.decode("utf-8"))
        value["candidate_id"] = "other"
        metadata_path.write_text(json.dumps(value), encoding="utf-8")
        with pytest.raises(OutputContractError):
            read_bundle(path)
        metadata_path.write_bytes(original)
        (path / "artwork.png").write_bytes((path / "artwork.png").read_bytes()[:-1])
        with pytest.raises(OutputContractError):
            read_bundle(path)
        with pytest.raises(BundleConflictError):
            write_bundle(build_export_bundle(result, "corruption"), temp)

    other = list(result.logical_grid)
    second = next(index for index, cell in enumerate(other[1:], start=1) if cell != other[0])
    other[0], other[second] = other[second], other[0]
    wrong_report = evaluate_grid(result.width, result.height, other)
    with pytest.raises(OutputContractError):
        build_export_bundle(result, "quality-mismatch", quality_report=wrong_report)


def test_m08_meaningful_grid_change_changes_artifact_identity() -> None:
    first = build_export_bundle(_mask_result(11), "identity")
    second = build_export_bundle(_mask_result(12), "identity")
    assert first.artwork.grid_hash != second.artwork.grid_hash
    assert first.artwork_json != second.artwork_json
    assert first.artwork_png != second.artwork_png
    assert first.metadata_json != second.metadata_json


def test_m08_all_difficulty_bands_and_59x59_round_trip() -> None:
    cases = (("EASY", 20, 21), ("MEDIUM", 30, 39), ("HARD", 40, 41), ("VERY_HARD", 59, 59))
    for index, (difficulty, width, height) in enumerate(cases):
        result = MaskSpriteGenerator().generate(GenerationRequest(difficulty, 100 + index, "MASK", width=width, height=height, style="ROBOT"))
        assert result.is_success
        bundle = build_export_bundle(result, f"band-{difficulty.lower()}")
        with TemporaryDirectory() as temp:
            restored = read_bundle(write_bundle(bundle, temp))
            assert (restored.artwork.width, restored.artwork.height) == (width, height)
            assert restored.artwork.cells == result.logical_grid


def test_m08_cross_process_hash_seed_json_and_png_bytes_are_stable() -> None:
    code = """import hashlib\nfrom scrubbots_pixel_factory import GenerationRequest\nfrom scrubbots_pixel_factory.generators.mask import MaskSpriteGenerator\nfrom scrubbots_pixel_factory.output import build_export_bundle\nr=MaskSpriteGenerator().generate(GenerationRequest('EASY',11,'MASK',width=20,height=20,style='ROBOT'))\nb=build_export_bundle(r,'cross-process')\nprint(hashlib.sha256(b.artwork_json+b.metadata_json+b.artwork_png).hexdigest())\n"""
    outputs = []
    for hash_seed in ("1", "random"):
        env = dict(os.environ, PYTHONHASHSEED=hash_seed, PYTHONPATH=str(ROOT / "src"))
        outputs.append(subprocess.check_output([sys.executable, "-c", code], text=True, env=env).strip())
    assert outputs[0] == outputs[1]
