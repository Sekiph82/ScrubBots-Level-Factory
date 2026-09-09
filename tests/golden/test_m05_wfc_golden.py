import json
from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest, GeneratorOptions
from scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCGenerator, WFCCandidate


ROOT = Path(__file__).parents[1]


def _exemplar(name: str) -> Exemplar:
    raw = json.loads((ROOT / "fixtures" / "wfc" / name).read_text(encoding="utf-8"))
    return Exemplar(raw["schema"], raw["version"], raw["exemplar_id"], raw["role"], raw["width"], raw["height"], tuple(raw["pixels"]), raw["provenance_type"], raw["provenance_description"], raw["ownership"])


def test_m05_golden_outputs_and_pattern_tables_are_stable() -> None:
    golden = json.loads((Path(__file__).with_name("m05_wfc_goldens.json")).read_text(encoding="utf-8"))
    for entry in golden["entries"]:
        exemplar = _exemplar(entry["exemplar"])
        request = GenerationRequest(entry["difficulty"], entry["seed"], "WFC", width=entry["dimensions"][0], height=entry["dimensions"][1], style=exemplar.exemplar_id, palette_subset=tuple(entry["used_palette"]), generator_options=GeneratorOptions("wfc", 1, entry["options"]))
        candidate = WFCGenerator(ExemplarRegistry((exemplar,))).generate_candidate(request)
        assert isinstance(candidate, WFCCandidate)
        assert candidate.result.digest() == entry["result_digest"]
        assert candidate.pattern_table.digest == entry["pattern_table_digest"]
        assert list(candidate.result.used_palette) == entry["used_palette"]
