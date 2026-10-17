from __future__ import annotations

import hashlib
import json
import base64
import io
import contextlib
import runpy
from unittest.mock import patch

from scrubbots_pixel_factory.supply_pipeline.current_game_contract import (
    CurrentGameContractDisposition as Disposition,
    REQUIRED_SOURCE_PATHS,
    evaluate_current_game_contract,
)


_COMMIT = "1" * 40


def _fixture_sources() -> dict[str, bytes]:
    contents = {
        "docs/01_GAMEPLAY_SPEC.md": b"Production board 20..59; rectangular boards allowed. C01..C16.",
        "docs/03_LEVEL_DATA_SPEC.md": (
            b"width: 20..59; height: 20..59; rectangular boards allowed. "
            b"Supply conservation, WIN (all non-VOID cells cleared), solver and Difficulty V1 measurements use artwork cells only."
        ),
        "scripts/data/level_data.gd": (
            b"const FORMAT_VERSION := 1\nconst FORMAT_VERSION_VOID := 2\nconst VOID_CELL := -1\n"
            b"func is_void(index: int) -> bool:\n\treturn version == FORMAT_VERSION_VOID and cells[index] == VOID_CELL\n"
        ),
        "scripts/data/level_loader.gd": b"const LevelValidator = preload(\"level_validator.gd\")\nstatic func load_from_text(text: String):\n",
        "scripts/gameplay/supply/supply_plan_loader.gd": (
            b"## The plan's 3, 4 or 5 FIFO columns\nconst MIN_COLUMNS := 3\nconst MAX_COLUMNS := 5\n"
            b"const VISIBLE_PREVIEW_DEPTH := 3\n"
        ),
        "scripts/gameplay/solver/proof_state.gd": b"# VOID cells (ADR-030) start CLEARED\n",
        "scripts/difficulty/level_difficulty_analyzer_v1.gd": b"var cells: int = level.get_artwork_cell_count()\n",
        "data/palettes/scrubbots_palette_v3.json": json.dumps(
            {"schema": "scrubbots-global-palette/v3", "colors": [
                {"id": f"C{i:02d}", "hex": f"#{i:02X}{i:02X}{i:02X}FF"} for i in range(1, 17)
            ]},
            separators=(",", ":"),
        ).encode(),
    }
    assert tuple(contents) == REQUIRED_SOURCE_PATHS
    return contents


def _authority(source_bytes: dict[str, bytes]) -> dict[str, object]:
    return {
        "repository": "Sekiph82/Scrubbots",
        "branch": "main",
        "commit": _COMMIT,
        "main_commit": _COMMIT,
        "source_commit_verified_as_main": True,
        "source_sha256": {path: hashlib.sha256(raw).hexdigest() for path, raw in source_bytes.items()},
    }


def test_current_game_contract_accepts_v1_v2_void_and_fifo_3_to_5() -> None:
    source_bytes = _fixture_sources()
    report = evaluate_current_game_contract(authority=_authority(source_bytes), source_bytes=source_bytes)

    assert report.disposition is Disposition.CURRENT_SOURCE_COMPATIBLE
    assert report.compatible is True
    assert report.contract["level_data"] == {"versions": [1, 2], "void_version": 2, "void_value": -1}
    assert report.contract["supply"] == {"fifo_columns": {"minimum": 3, "maximum": 5}, "visible_preview_depth": 3}
    assert report.contract["global_palette_ids"] == [f"C{i:02d}" for i in range(1, 17)]
    assert len(report.source_sha256) == len(REQUIRED_SOURCE_PATHS)
    assert report.to_dict()["runtime_executed"] is False


def test_contract_fails_closed_when_source_bytes_do_not_match_inventory() -> None:
    source_bytes = _fixture_sources()
    authority = _authority(source_bytes)
    source_bytes["scripts/data/level_data.gd"] = source_bytes["scripts/data/level_data.gd"] + b"# changed"

    report = evaluate_current_game_contract(authority=authority, source_bytes=source_bytes)

    assert report.disposition is Disposition.SOURCE_HASH_MISMATCH
    assert report.compatible is False


def test_contract_distinguishes_stale_or_unattested_main() -> None:
    source_bytes = _fixture_sources()
    stale = _authority(source_bytes)
    stale["main_commit"] = "2" * 40
    stale_report = evaluate_current_game_contract(authority=stale, source_bytes=source_bytes)
    assert stale_report.disposition is Disposition.SOURCE_VERSION_DRIFT

    unattested = _authority(source_bytes)
    unattested["source_commit_verified_as_main"] = False
    unverified_report = evaluate_current_game_contract(authority=unattested, source_bytes=source_bytes)
    assert unverified_report.disposition is Disposition.CURRENT_GAME_UNVERIFIED


def test_contract_reports_missing_inputs_and_semantic_drift() -> None:
    missing = evaluate_current_game_contract(authority=None, source_bytes=None)
    assert missing.disposition is Disposition.CURRENT_GAME_UNVERIFIED

    source_bytes = _fixture_sources()
    source_bytes["scripts/gameplay/supply/supply_plan_loader.gd"] = b"const MIN_COLUMNS := 2\nconst MAX_COLUMNS := 5\nconst VISIBLE_PREVIEW_DEPTH := 3\n"
    report = evaluate_current_game_contract(authority=_authority(source_bytes), source_bytes=source_bytes)
    assert report.disposition is Disposition.CURRENT_GAME_CONTRACT_DRIFT
    assert "CONTRACT_FIELD_MISMATCH:fifo_columns" in report.reason_codes


def _level_and_plan(*, version: int = 1, void_count: int = 0) -> tuple[bytes, bytes]:
    each_color = 100 if void_count else 200
    half = each_color // 2
    cells = [-1] * void_count + [0] * each_color + [1] * each_color
    level = {"id": "fixture-001", "version": version, "width": 20, "height": 20,
             "cells": cells, "palette": ["#010101FF", "#020202FF"]}
    plan = {"schema": "scrubbots.level_supply_plan.v1", "version": 1, "levelId": "fixture-001",
            "columnCount": 3, "visiblePreviewDepth": 3, "maxRobotsPerBatch": 200,
            "columns": [[{"cid": "C01", "robots": half}],
                        [{"cid": "C01", "robots": half}, {"cid": "C02", "robots": half}],
                        [{"cid": "C02", "robots": half}]]}
    return json.dumps(level, separators=(",", ":")).encode(), json.dumps(plan, separators=(",", ":")).encode()


def _snapshot() -> dict[str, object]:
    sources = _fixture_sources()
    level, plan = _level_and_plan()
    return {"candidate_id": "fixture-candidate", "authority": _authority(sources),
            "source_bytes_b64": {path: base64.b64encode(raw).decode("ascii") for path, raw in sources.items()},
            "level_data_b64": base64.b64encode(level).decode("ascii"),
            "supply_plan_b64": base64.b64encode(plan).decode("ascii")}


def test_readiness_path_exposes_static_preflight_without_changing_gate_decision() -> None:
    from scrubbots_pixel_factory import studio_extensions
    from scrubbots_pixel_factory.supply_pipeline.current_game_contract import preflight_json_snapshot
    snapshot = _snapshot()
    candidate = {"candidate_id": "fixture-candidate", "artwork_sha256": "a" * 64,
                 "grid_hash": preflight_json_snapshot(snapshot)["logical_grid_hash"],
                 "quality": {"decision": "ACCEPT", "grid_hash": preflight_json_snapshot(snapshot)["logical_grid_hash"]}}
    with (patch.object(studio_extensions, "list_candidates", return_value=[candidate]),
          patch.object(studio_extensions, "_latest_review", return_value=None),
          patch.object(studio_extensions, "_validated_review_chain", return_value=([], [])),
          patch.object(studio_extensions, "_latest_ready_pipeline", return_value=None)):
        card = studio_extensions.readiness_card("fixture-candidate", snapshot)
        missing = studio_extensions.readiness_card("fixture-candidate")
    assert card["overall"] == missing["overall"] == "NOT READY"
    assert card["current_game_preflight"]["disposition"] == "SOURCE_CONTRACT_COMPATIBLE_NOT_REPLAYED"
    assert card["current_game_preflight"]["solver_invocations"] == 0
    assert missing["current_game_preflight"]["disposition"] == Disposition.CURRENT_GAME_UNVERIFIED.value
    assert card["current_main_replay_bridge"]["disposition"] == "CPX002_AUTHORITY_REQUIRED"
    assert card["current_main_replay_bridge"]["reason_codes"] == ["CURRENT_MAIN_RUNTIME_NOT_EXECUTED"]
    launcher = open("level_factory/scripts/factory_core_launcher.py", encoding="utf-8").read()
    assert 'request.get("current_game_preflight")' in launcher
    assert 'extensions.readiness_card(' in launcher
    launcher_api = runpy.run_path("level_factory/scripts/factory_core_launcher.py")
    output = io.StringIO()
    request = json.dumps({"candidate_id": "fixture-candidate", "current_game_preflight": snapshot})
    with patch.object(studio_extensions, "readiness_card", return_value={"reached": True}) as readiness_call, \
         contextlib.redirect_stdout(output):
        exit_code = launcher_api["_studio_extension_main"](["--operation", "readiness", "--request-json", request])
    assert exit_code == 0
    assert readiness_call.call_args.args[0] == "fixture-candidate"
    assert readiness_call.call_args.args[1]["authority"]["commit"] == _COMMIT
    assert json.loads(output.getvalue())["reached"] is True


def test_static_preflight_rejects_void_on_v1_and_bad_fifo_without_runtime() -> None:
    from scrubbots_pixel_factory.supply_pipeline.current_game_contract import preflight_level_supply_bytes
    sources = _fixture_sources()
    report = evaluate_current_game_contract(authority=_authority(sources), source_bytes=sources)
    v1_level, plan = _level_and_plan(version=1, void_count=1)
    rejected_v1 = preflight_level_supply_bytes(contract_report=report, level_data_bytes=v1_level, supply_plan_bytes=plan)
    assert rejected_v1["disposition"] == "STATIC_CONTRACT_REJECTED"
    assert "VOID_REQUIRES_LEVEL_DATA_V2" in rejected_v1["reason_codes"]
    level, bad_plan = _level_and_plan()
    bad_plan_data = json.loads(bad_plan)
    bad_plan_data["columnCount"] = 2
    rejected_fifo = preflight_level_supply_bytes(contract_report=report, level_data_bytes=level,
                                                 supply_plan_bytes=json.dumps(bad_plan_data).encode())
    assert "FIFO_COLUMN_COUNT_OUTSIDE_CURRENT_GAME_RANGE" in rejected_fifo["reason_codes"]
    assert rejected_fifo["solver_invocations"] == 0


def test_v2_void_and_cpx002_bridge_remain_static_until_authorized_replay() -> None:
    from scrubbots_pixel_factory.supply_pipeline.current_game_contract import (
        current_main_replay_bridge, preflight_level_supply_bytes,
    )
    sources = _fixture_sources()
    report = evaluate_current_game_contract(authority=_authority(sources), source_bytes=sources)
    level, plan = _level_and_plan(version=2, void_count=200)
    static = preflight_level_supply_bytes(contract_report=report, level_data_bytes=level, supply_plan_bytes=plan)
    assert static["compatible"] is True
    assert static["void_cell_count"] == 200
    bridge = current_main_replay_bridge(current_game_preflight=static,
                                        owner_provenance={"compatible": True},
                                        cpx002_authority=None, replay_evidence=None)
    assert bridge["disposition"] == "CPX002_AUTHORITY_REQUIRED"
    assert "EXPLICIT_ISOLATED_TEMP_SCRUBBOTS_PROJECT_AUTHORITY" in bridge["missing_evidence"]
    assert bridge["runtime_executed"] is False
    assert bridge["solver_invocations"] == 0


def test_owner_provenance_adapter_fails_closed_for_test_candidates_without_mutation() -> None:
    from pathlib import Path
    from types import SimpleNamespace
    from scrubbots_pixel_factory.supply_pipeline import release_pool
    from scrubbots_pixel_factory.supply_pipeline.release_pool import ReleaseError
    repo = Path.cwd()
    fake_record = SimpleNamespace(
        resolve=lambda: repo / "synthetic-source.json",
        is_symlink=lambda: False,
        stat=lambda: SimpleNamespace(st_size=12),
        read_bytes=lambda: b'{"fixture":true}',
    )
    candidate = {"candidate_id": "test-candidate", "metadata": {"generator_metadata": {
        "classification": {"candidate_class": "TEST"}}}}
    with patch.object(release_pool, "_candidate_source_lineage", return_value={"source_id": "source-1"}), \
         patch.object(release_pool, "validate_pool_candidate_provenance",
                      side_effect=ReleaseError("TEST candidate cannot enter the production Release Pool")), \
         patch("scrubbots_pixel_factory.studio_extensions._source_record_paths", return_value=(fake_record, None)):
        result = release_pool.inspect_current_game_candidate_provenance(candidate, None, None, None)
    assert result["disposition"] == "OWNER_PROVENANCE_REJECTED"
    assert result["release_pool_mutated"] is False
    assert result["runtime_executed"] is False


def test_release_pool_provenance_requires_exact_current_owner_accept() -> None:
    from scrubbots_pixel_factory.contracts.candidate_provenance import CandidateClass
    from scrubbots_pixel_factory.supply_pipeline import release_pool
    lineage = {"source_id": "owner-upload-" + "c" * 64, "source_sha256": "c" * 64,
               "source_record": "level_factory/output/owner-uploads/owner-upload-" + "c" * 64 + "/source.json",
               "source_bytes_unchanged": True,
               "derivation": "EXACT_LOGICAL_OWNER_UPLOAD_TO_CANONICAL_CANDIDATE"}
    classification = {"candidate_class": "PRODUCTION_CANDIDATE", "source_sha256": "c" * 64}
    candidate = {"candidate_id": "owner-candidate", "grid_hash": "e" * 64, "artwork_sha256": "f" * 64,
                 "metadata": {"generation": {"result": {}}, "generator_metadata": {
                     "classification": classification,
                     "payload": {"namespace": "owner-upload", "data": {"source_lineage": lineage}}}}}
    with patch.object(release_pool, "_verify_candidate_source_grid_binding", return_value="c" * 64), \
         patch("scrubbots_pixel_factory.supply_pipeline.release_pool.validate_verified_owner_upload_classification",
               return_value=CandidateClass.PRODUCTION_CANDIDATE):
        try:
            release_pool.validate_pool_candidate_provenance(candidate, None)
        except release_pool.ReleaseError as exc:
            assert "exact current owner ACCEPT" in str(exc)
        else:
            raise AssertionError("missing current owner ACCEPT unexpectedly passed")


def test_owner_provenance_reports_record_digest_but_requires_current_ready_load_check() -> None:
    from pathlib import Path
    from types import SimpleNamespace
    from scrubbots_pixel_factory.supply_pipeline import release_pool
    repo = Path.cwd()
    raw_record = b'{"fixture":"source-record"}'
    fake_record = SimpleNamespace(
        resolve=lambda: repo / "synthetic-source.json",
        is_symlink=lambda: False,
        stat=lambda: SimpleNamespace(st_size=len(raw_record)),
        read_bytes=lambda: raw_record,
    )
    candidate = {"candidate_id": "owner-candidate", "grid_hash": "grid-1", "metadata": {"generator_metadata": {
        "classification": {"candidate_class": "PRODUCTION_CANDIDATE"}}}}
    verified_classification = {"candidate_class": "PRODUCTION_CANDIDATE", "source_sha256": "c" * 64}
    review = {"review_id": "review-owner-candidate-0001", "disposition": "ACCEPT"}
    ready = {"disposition": "READY", "primary": {"state": "READY",
             "load_check": {"state": "READY", "disposition": "READY"},
             "source_record_sha256": hashlib.sha256(raw_record).hexdigest()}}
    static = {"compatible": True, "candidate_id": "owner-candidate", "logical_grid_hash": "grid-1"}
    with patch.object(release_pool, "_candidate_source_lineage", return_value={"source_id": "source-1"}), \
         patch.object(release_pool, "validate_pool_candidate_provenance", return_value=verified_classification), \
         patch("scrubbots_pixel_factory.studio_extensions._source_record_paths", return_value=(fake_record, None)):
        result = release_pool.inspect_current_game_candidate_provenance(candidate, review, ready, static)
        mismatched = release_pool.inspect_current_game_candidate_provenance(
            candidate, review, ready, {**static, "logical_grid_hash": "different-grid"})
        record_mismatch = release_pool.inspect_current_game_candidate_provenance(
            candidate, review, {"disposition": "READY", "primary": {**ready["primary"],
            "source_record_sha256": "d" * 64}}, static)
    assert result["disposition"] == "OWNER_PROVENANCE_VERIFIED_STATIC_ONLY"
    assert result["source_sha256"] == "c" * 64
    assert result["source_record_sha256"] == hashlib.sha256(raw_record).hexdigest()
    assert result["runtime_executed"] is False
    assert result["compatible"] is True
    assert mismatched["disposition"] == "OWNER_PROVENANCE_VERIFIED_CURRENT_GAME_NOT_READY"
    assert "CURRENT_GAME_STATIC_PREFLIGHT_MUST_MATCH_SELECTED_CANDIDATE_GRID" in mismatched["reason_codes"]
    assert record_mismatch["disposition"] == "OWNER_PROVENANCE_REJECTED"
    assert result["release_pool_mutated"] is False
