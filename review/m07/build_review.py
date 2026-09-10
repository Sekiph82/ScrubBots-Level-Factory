"""Build the committed deterministic M07 review pack.

The hand-authored cases are deliberately synthetic structural fixtures. The
MASK, RULES, HYBRID and synthetic-test-exemplar WFC cases are representative
generator outputs; no owner-approved WFC exemplar is claimed or added.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from scrubbots_pixel_factory import GenerationRequest, GeneratorOptions  # noqa: E402
from scrubbots_pixel_factory.generators.mask import MaskSpriteGenerator  # noqa: E402
from scrubbots_pixel_factory.generators.rules import RuleShapeGenerator  # noqa: E402
from scrubbots_pixel_factory.generators.router import HybridGenerator  # noqa: E402
from scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCGenerator  # noqa: E402
from scrubbots_pixel_factory.quality import QualityPolicy, ReviewEntry, write_review_pack  # noqa: E402


def _central_symmetric(width: int, height: int, body: str = "C02", accent: str = "C03") -> list[str]:
    cells = ["C01"] * (width * height)
    left, right = (width - 8) // 2, (width - 8) // 2 + 7
    top, bottom = (height - 10) // 2, (height - 10) // 2 + 9
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            cells[y * width + x] = body
    for y in (top + 4, top + 5):
        for x in (left + 3, left + 4):
            cells[y * width + x] = accent
    return cells


def _sparse_islands(width: int, height: int) -> list[str]:
    cells = ["C01"] * (width * height)
    for y in range(3, 7):
        for x in range(3, 7):
            cells[y * width + x] = "C02"
    for y in range(height - 7, height - 3):
        for x in range(width - 7, width - 3):
            cells[y * width + x] = "C03"
    return cells


def _central_subject(width: int, height: int) -> list[str]:
    cells = _central_symmetric(width, height, "C02", "C03")
    cells[(height // 2 - 4) * width + (width // 2 + 2)] = "C04"
    return cells


def _multi_island(width: int, height: int) -> list[str]:
    cells = ["C01"] * (width * height)
    for y in range(7, 12):
        for x in range(2, 7):
            cells[y * width + x] = "C04"
        for x in range(width - 7, width - 2):
            cells[y * width + x] = "C05"
    return cells


def _asymmetric_organic(width: int, height: int) -> list[str]:
    cells = ["C01"] * (width * height)
    for y in range(4, height - 4):
        start = 4 + (y - 4) // 3
        end = min(width - 4, 11 + ((y * 2) % 5))
        for x in range(start, end + 1):
            cells[y * width + x] = "C06"
    for y, x in ((7, 8), (8, 8), (9, 9), (10, 9), (11, 10)):
        cells[y * width + x] = "C07"
    return cells


def _diversity_fixture(width: int, height: int) -> list[str]:
    cells = ["C01"] * (width * height)
    for y in range(height // 2 - 2, height // 2 + 2):
        for x in range(4, width - 4):
            cells[y * width + x] = "C08"
    for x in range(width // 2 - 1, width // 2 + 1):
        for y in range(height // 2 - 5, height // 2 + 5):
            cells[y * width + x] = "C09"
    return cells


def _checkerboard(width: int, height: int) -> list[str]:
    return [f"C{1 + ((x + y) % 2):02d}" for y in range(height) for x in range(width)]


def _entries() -> list[ReviewEntry]:
    entries: list[ReviewEntry] = []
    entries.append(ReviewEntry("bad-01-inferred-empty", 20, 20, ["C01"] * 400, mode="FIXTURE", seed="bad-empty", classification="REJECTION_FIXTURE"))
    slab = ["C01"] * 400
    for y in range(1, 19):
        for x in range(1, 19):
            slab[y * 20 + x] = "C02"
    entries.append(ReviewEntry("bad-02-full-slab", 20, 20, slab, mode="FIXTURE", seed="bad-slab", classification="REJECTION_FIXTURE"))
    salt = ["C01"] * 400
    for index in (105, 107, 145, 147, 252, 254, 292, 294):
        salt[index] = "C02"
    entries.append(ReviewEntry("bad-03-salt-and-pepper", 20, 20, salt, mode="FIXTURE", seed="bad-salt", classification="REJECTION_FIXTURE"))
    fragments = ["C01"] * 400
    for index in (84, 86, 314, 316):
        fragments[index] = "C02"
    entries.append(ReviewEntry("bad-04-tiny-fragments", 20, 20, fragments, mode="FIXTURE", seed="bad-fragments", classification="REJECTION_FIXTURE"))
    entries.append(ReviewEntry("bad-05-checkerboard", 20, 20, _checkerboard(20, 20), mode="FIXTURE", seed="bad-checker", classification="REJECTION_FIXTURE"))
    dominance = ["C01"] * 400
    for y in range(1, 19):
        for x in range(1, 19):
            dominance[y * 20 + x] = "C02"
    dominance[190] = "C03"
    entries.append(
        ReviewEntry(
            "bad-06-dominance",
            20,
            20,
            dominance,
            mode="FIXTURE",
            seed="bad-dominance",
            classification="REJECTION_FIXTURE",
            policy=QualityPolicy(max_color_dominance_ratio=0.80, max_largest_region_ratio=1.0),
        )
    )
    entries.append(ReviewEntry("bad-07-off-palette", 20, 20, ["BG01"] * 400, mode="FIXTURE", seed="bad-palette", classification="INVALID_INPUT_FIXTURE"))
    entries.append(ReviewEntry("bad-08-dimension-mismatch", 20, 20, ["C01"] * 399, mode="FIXTURE", seed="bad-dimensions", classification="INVALID_INPUT_FIXTURE"))
    duplicate = _diversity_fixture(20, 20)
    near_duplicate = list(duplicate)
    near_duplicate[190] = "C04"
    entries.append(ReviewEntry("bad-09-exact-duplicate-a", 20, 20, duplicate, mode="FIXTURE", seed="duplicate-a", classification="DIVERSITY_FIXTURE"))
    entries.append(ReviewEntry("bad-10-exact-duplicate-b", 20, 20, duplicate, mode="FIXTURE", seed="duplicate-b", classification="DIVERSITY_FIXTURE"))
    entries.append(ReviewEntry("bad-11-near-duplicate", 20, 20, near_duplicate, mode="FIXTURE", seed="near-duplicate", classification="DIVERSITY_FIXTURE"))

    entries.extend((
        ReviewEntry("good-01-central-subject", 20, 20, _central_subject(20, 20), mode="FIXTURE", seed="central", classification="CONNECTED_CENTRAL_SUBJECT"),
        ReviewEntry("good-02-sparse", 20, 20, _sparse_islands(20, 20), mode="FIXTURE", seed="sparse", classification="SPARSE_NEGATIVE_SPACE"),
        ReviewEntry("good-03-multi-island", 20, 20, _multi_island(20, 20), mode="FIXTURE", seed="multi-island", classification="MULTI_ISLAND"),
        ReviewEntry("good-04-symmetric", 20, 20, _central_symmetric(20, 20), mode="FIXTURE", seed="symmetric", classification="SYMMETRIC_SUBJECT"),
        ReviewEntry("good-05-asymmetric-organic", 20, 20, _asymmetric_organic(20, 20), mode="FIXTURE", seed="asymmetric", classification="ASYMMETRIC_ORGANIC"),
        ReviewEntry("good-06-rectangular", 23, 20, _central_symmetric(23, 20), mode="FIXTURE", seed="rectangular", classification="RECTANGULAR_SUBJECT"),
    ))

    mask = MaskSpriteGenerator()
    rules = RuleShapeGenerator()
    hybrid = HybridGenerator()
    for index, seed in enumerate((11, 23, 47), start=1):
        mask_result = mask.generate(GenerationRequest("EASY", seed, "MASK", width=20, height=20, style="ROBOT"))
        if mask_result.is_success:
            entries.append(ReviewEntry(f"generated-{index:02d}-mask", 20, 20, mask_result.logical_grid, mode="MASK", seed=seed, difficulty="EASY", classification="GENERATED_M03"))
        rules_result = rules.generate(GenerationRequest("EASY", seed, "RULES", width=20, height=20, style="ORGANIC"))
        if rules_result.is_success:
            entries.append(ReviewEntry(f"generated-{index:02d}-rules", 20, 20, rules_result.logical_grid, mode="RULES", seed=seed, difficulty="EASY", classification="GENERATED_M04"))
        hybrid_request = GenerationRequest(
            "EASY",
            seed,
            "HYBRID",
            width=20,
            height=20,
            generator_options=GeneratorOptions(
                "hybrid",
                1,
                {
                    "strategy": "MASK_GEOMETRY_RULE_COLOR_REGIONS",
                    "mask_style": "ROBOT",
                    "rules_style": "ORGANIC",
                    "mask_symmetry": "HORIZONTAL",
                },
            ),
        )
        hybrid_result = hybrid.generate(hybrid_request)
        if hybrid_result.is_success:
            entries.append(ReviewEntry(f"generated-{index:02d}-hybrid", 20, 20, hybrid_result.logical_grid, mode="HYBRID", seed=seed, difficulty="EASY", classification="GENERATED_M06"))

    raw = json.loads((REPO_ROOT / "tests" / "fixtures" / "wfc" / "wfc-synthetic-easy-3.json").read_text(encoding="utf-8"))
    exemplar = Exemplar(
        raw["schema"], raw["version"], raw["exemplar_id"], raw["role"], raw["width"], raw["height"],
        tuple(raw["pixels"]), raw["provenance_type"], raw["provenance_description"], raw["ownership"],
    )
    wfc_policy = QualityPolicy(max_isolated_ratio=1.0, max_tiny_cell_ratio=1.0, max_color_dominance_ratio=1.0)
    wfc = WFCGenerator(ExemplarRegistry((exemplar,)))
    for index, seed in enumerate((11, 23), start=1):
        request = GenerationRequest(
            "EASY", seed, "WFC", width=20, height=20, style=exemplar.exemplar_id,
            palette_subset=exemplar.source_palette,
            generator_options=GeneratorOptions("wfc", 1, {"pattern_size": 2, "input_periodic": True}),
        )
        result = wfc.generate(request)
        if result.is_success:
            entries.append(ReviewEntry(f"generated-{index + 20:02d}-wfc-synthetic-test", 20, 20, result.logical_grid, mode="WFC", seed=seed, difficulty="EASY", classification="GENERATED_M05_SYNTHETIC_TEST_ONLY", policy=wfc_policy))
    return entries


def build() -> tuple[Path, Path]:
    entries = _entries()
    if len(entries) < 20:
        raise RuntimeError(f"M07 review pack requires at least 20 entries, got {len(entries)}")
    return write_review_pack(entries, REPO_ROOT / "review" / "m07")


if __name__ == "__main__":
    manifest, contact_sheet = build()
    print(f"wrote {manifest}")
    print(f"wrote {contact_sheet}")
