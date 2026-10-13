from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import patch

from scrubbots_pixel_factory import studio_extensions as studio
from scrubbots_pixel_factory.supply_pipeline import game_rules, scrubpack_identity, supply_exporter, supply_optimizer, verify


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_two_fake_successful_same_source_runs_keep_three_and_four_column_artifacts(tmp_path, monkeypatch):
    extensions = tmp_path / "studio-extensions"
    monkeypatch.setattr(studio, "extensions_root", lambda: extensions)
    monkeypatch.setattr(studio, "_canonical_cells_to_grid", lambda cells, width, height, rules: ({"grid": cells}, ["C01"]))

    class FakeRules:
        def __init__(self, _project, column_count):
            self.column_count = column_count
            self.attestation = None
            self.authority = {"test_fixture": True}

    class FakeOptimizer:
        def __init__(self, rules):
            self.rules = rules

        def run_grid(self, *_args, **_kwargs):
            return {
                "solver_status": "SOLVED", "solution_final": "WIN", "difficulty": "MEDIUM",
                "difficulty_score": 50.0, "difficulty_basis": "ScrubBots Difficulty V1 fixture",
                "fixture_column_count": self.rules.column_count,
            }

    class FakeExporter:
        def __init__(self, rules):
            self.rules = rules

        def export(self, result, output_dir, level_id):
            directory = Path(output_dir)
            directory.mkdir(parents=True)
            files = {}
            for name, value in (("level", {"columns": self.rules.column_count, "id": level_id}),
                                ("supply_plan", {"columns": self.rules.column_count}),
                                ("result", result)):
                path = directory / f"{name}.json"
                path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
                files[name] = str(path)
            return files

    class FakeModule:
        @staticmethod
        def verify_exported_supply(*_args, **_kwargs):
            return {"state": "READY", "disposition": "PASS"}

    monkeypatch.setattr(game_rules, "GameRules", FakeRules)
    monkeypatch.setattr(supply_optimizer, "SupplyOptimizer", FakeOptimizer)
    monkeypatch.setattr(supply_exporter, "SupplyExporter", FakeExporter)
    monkeypatch.setattr(verify, "verify_exported_supply", FakeModule.verify_exported_supply)
    monkeypatch.setattr(scrubpack_identity, "derive_solver_supply_identity", lambda *_args: {"identity_sha256": "fixture"})

    def write_direct(path, payload, *, immutable=False):
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = studio._canonical_bytes(payload)
        if immutable and path.exists() and path.read_bytes() != raw:
            raise AssertionError("immutable test pipeline collision")
        path.write_bytes(raw)

    monkeypatch.setattr(studio, "_write_json", write_direct)
    outputs = []
    pipelines = []
    for activity_id, columns in (("activity-three", 3), ("activity-four", 4)):
        pipeline = studio._run_canonical_artwork_route(
            identity="candidate-same-source", cells=["C01"], width=1, height=1,
            evidence="test fixture", request={"activity_run_id": activity_id, "column_count": columns},
            source_kind="OWNER_UPLOAD",
        )
        assert pipeline["disposition"] == "READY"
        assert pipeline["primary"]["column_count"] == columns
        pipelines.append(pipeline)
        outputs.append({key: Path(value) for key, value in pipeline["primary"]["files"].items()})

    first_hashes = {key: _sha(path) for key, path in outputs[0].items()}
    second_hashes = {key: _sha(path) for key, path in outputs[1].items()}
    assert set(first_hashes) == {"level", "supply_plan", "result"}
    assert outputs[0]["level"].parent != outputs[1]["level"].parent
    assert json.loads(outputs[0]["level"].read_text())["columns"] == 3
    assert json.loads(outputs[1]["level"].read_text())["columns"] == 4
    assert {key: _sha(path) for key, path in outputs[0].items()} == first_hashes
    assert {key: _sha(path) for key, path in outputs[1].items()} == second_hashes
    for pipeline, files, hashes in zip(pipelines, outputs, (first_hashes, second_hashes), strict=True):
        for key, path in files.items():
            assert pipeline["primary"]["files"][key] == str(path)
            assert _sha(path) == hashes[key]
