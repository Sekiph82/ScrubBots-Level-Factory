import json
import hashlib
from pathlib import Path

from scrubbots_pixel_factory import GenerationRequest, GeneratorOptions
from scrubbots_pixel_factory.generators.wfc import Exemplar, ExemplarRegistry, WFCGenerator, WFCCandidate


ROOT = Path(__file__).parents[1]


def _exemplar(exemplar_id: str) -> Exemplar:
    name = f"{exemplar_id}.json"
    raw = json.loads((ROOT / "fixtures" / "wfc" / name).read_text(encoding="utf-8"))
    return Exemplar(raw["schema"], raw["version"], raw["exemplar_id"], raw["role"], raw["width"], raw["height"], tuple(raw["pixels"]), raw["provenance_type"], raw["provenance_description"], raw["ownership"])


def test_m05_golden_outputs_and_pattern_tables_are_stable() -> None:
    golden = json.loads((Path(__file__).with_name("m05_wfc_goldens.json")).read_text(encoding="utf-8"))
    for entry in golden["entries"]:
        exemplar = _exemplar(entry["exemplar_id"])
        request = GenerationRequest(entry["difficulty"], entry["seed"], "WFC", width=entry["dimensions"][0], height=entry["dimensions"][1], style=exemplar.exemplar_id, palette_subset=tuple(pair[1] for pair in entry["palette_mapping"]), generator_options=GeneratorOptions("wfc", 1, entry["options"]))
        candidate = WFCGenerator(ExemplarRegistry((exemplar,))).generate_candidate(request)
        assert isinstance(candidate, WFCCandidate)
        assert candidate.exemplar.digest == entry["exemplar_digest"]
        assert candidate.result.digest() == entry["result_digest"]
        assert hashlib.sha256("".join(candidate.logical_grid).encode()).hexdigest() == entry["output_grid_digest"]
        assert candidate.pattern_table.digest == entry["pattern_table_digest"]
        assert list(candidate.result.used_palette) == [pair[1] for pair in entry["palette_mapping"]]
        assert candidate.wfc_metadata["raw_extracted_window_count"] == entry["raw_extracted_window_count"]
        assert candidate.wfc_metadata["transformed_observation_count"] == entry["transformed_observation_count"]
        assert candidate.wfc_metadata["unique_pattern_count"] == entry["unique_pattern_count"]
        assert candidate.wfc_metadata["attempt"] == entry["attempt"]
        assert candidate.wfc_metadata["contradiction_history"] == entry["contradiction_history"]
