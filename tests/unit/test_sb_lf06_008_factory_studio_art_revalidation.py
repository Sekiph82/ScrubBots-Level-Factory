from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from scrubbots_pixel_factory import GenerationRequest, QualityPolicy, evaluate_grid, logical_grid_hash
from scrubbots_pixel_factory.generators.mask import MaskSpriteGenerator
from scrubbots_pixel_factory.output import build_export_bundle, write_bundle


ROOT = Path(__file__).resolve().parents[2]
FACTORY = ROOT / "level_factory"
GATEWAY = FACTORY / "scripts" / "factory_core_gateway.gd"
LAUNCHER = FACTORY / "scripts" / "factory_core_launcher.py"
EDITOR = FACTORY / "scripts" / "factory_studio_art_editor.gd"
REVALIDATION = FACTORY / "scripts" / "factory_studio_art_revalidation.gd"
TARGET = FACTORY / "scripts" / "factory_studio_target_controls.gd"
INTEGRATION = FACTORY / "tests" / "factory_studio_art_revalidation_integration_suite.gd"
TEST_ROOT = FACTORY / "output" / ".lf06-008-python-revalidation-test"


def _invoke(request: dict[str, object], request_path: Path) -> subprocess.CompletedProcess[str]:
    request_path.write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(LAUNCHER), "studio-revalidate-art", "--request-file", str(request_path)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def _source_fixture() -> tuple[Path, dict[str, object], bytes, bytes, bytes]:
    shutil.rmtree(TEST_ROOT, ignore_errors=True)
    result = MaskSpriteGenerator().generate(
        GenerationRequest("EASY", 11, "MASK", width=20, height=20, style="ROBOT")
    )
    report = evaluate_grid(result.width, result.height, result.logical_grid, policy=QualityPolicy(difficulty="EASY"))
    bundle = build_export_bundle(result, "lf06-008-python-source", quality_report=report)
    candidate = write_bundle(bundle, TEST_ROOT)
    request = {
        "schema": "scrubbots-studio-manual-art-revalidation",
        "schema_version": 1,
        "operation": "manual-art-structural-revalidation",
        "source_bundle_path": str(candidate),
        "source_candidate_id": bundle.artwork.candidate_id,
        "source_artwork_sha256": hashlib.sha256(bundle.artwork_png).hexdigest(),
        "source_width": bundle.artwork.width,
        "source_height": bundle.artwork.height,
        "source_cells": list(bundle.artwork.cells),
        "working_width": bundle.artwork.width,
        "working_height": bundle.artwork.height,
        "working_cells": list(bundle.artwork.cells),
        "dirty_cell_count": 0,
    }
    return candidate, request, bundle.artwork_png, bundle.artwork_json, bundle.metadata_json


def test_revalidation_component_is_bounded_and_scope_qualified() -> None:
    source = REVALIDATION.read_text(encoding="utf-8")
    lowered = source.lower()
    assert 'class_name factorystudioartrevalidation' in lowered
    assert 'structural art qa only — not full gameplay validation' in lowered
    assert 'solver: unavailable pending m03' in lowered
    assert 'measured difficulty: unavailable pending m04' in lowered
    assert 'unified validation: unavailable pending m05' in lowered
    assert 'qa pass != owner accept' in lowered
    assert 'func configure_editor' in lowered
    assert 'func snapshot' in lowered
    assert 'func refresh_from_editor' in lowered
    assert 'func _process' in lowered
    assert 'stale' in lowered
    assert 'revalidate manual artwork' in lowered
    assert '_result_current = false' in lowered
    assert '_state not in [running, stale]' in lowered
    assert '_state not in [available, stale]' in lowered
    assert 'evaluate_grid' not in lowered
    assert 'qualitypolicy' not in lowered
    assert 'store_buffer' not in lowered
    for marker in ("cmd /c", "powershell", "bash", "httprequest", "http://", "https://", "api_key", "credential", "provider"):
        assert marker not in lowered


def test_editor_exposes_only_read_only_logical_snapshots_for_revalidation() -> None:
    source = EDITOR.read_text(encoding="utf-8")
    assert "source_logical_cells_snapshot" in source
    assert "working_logical_cells_snapshot" in source
    assert "canonical_color_id_for_pixel" in source
    assert "FileAccess.WRITE" not in source
    assert "evaluate_grid" not in source
    assert "generationrequest" not in source.lower()


def test_gateway_and_launcher_use_fixed_discrete_revalidation_operation() -> None:
    gateway = GATEWAY.read_text(encoding="utf-8").lower()
    launcher = LAUNCHER.read_text(encoding="utf-8").lower()
    assert 'studio-revalidate-art' in gateway
    assert 'os.execute' in gateway
    assert 'packedstringarray' in gateway
    assert 'request.json' in gateway
    assert 'studio-revalidate-art' in launcher
    assert 'read_bundle' in launcher
    assert 'qualitypolicy' in launcher
    assert 'evaluate_grid' in launcher
    assert 'logical_grid_hash' in launcher
    assert 'cmd /c' not in gateway and 'powershell' not in gateway and 'bash' not in gateway
    assert 'sys.argv[1]' in launcher
    assert 'canonical_main()' in launcher
    assert 'subprocess' not in launcher


def test_python_bridge_reuses_source_policy_and_canonical_hashes() -> None:
    candidate, request, artwork_png, artwork_json, metadata_json = _source_fixture()
    try:
        source_cells = list(request["source_cells"])
        alternate = next(color for color in ("C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16") if color != source_cells[0])
        working_cells = list(source_cells)
        working_cells[0] = alternate
        request["working_cells"] = working_cells
        request["dirty_cell_count"] = 1
        result = _invoke(request, TEST_ROOT / "request.json")
        assert result.returncode == 0, result.stdout + result.stderr
        payload = json.loads(result.stdout)
        assert payload["state"] == "RESULT"
        assert payload["scope"] == "STRUCTURAL_ART_QA_ONLY"
        assert payload["source_candidate_id"] == request["source_candidate_id"]
        assert payload["working_grid_hash"] == logical_grid_hash(20, 20, working_cells)
        source_metadata = json.loads(metadata_json.decode("utf-8"))
        source_policy = source_metadata["quality"]["report"]["policy"]
        assert payload["source_quality_policy"] == source_policy
        expected = evaluate_grid(20, 20, working_cells, policy=QualityPolicy(**source_policy)).as_dict()
        assert payload["quality_report"] == expected
        assert payload["decision"] == ("ACCEPT" if expected["accepted"] else "REJECT")
        assert (candidate / "artwork.png").read_bytes() == artwork_png
        assert (candidate / "artwork.json").read_bytes() == artwork_json
        assert (candidate / "metadata.json").read_bytes() == metadata_json
    finally:
        shutil.rmtree(TEST_ROOT, ignore_errors=True)


def test_python_bridge_rejects_clean_malformed_and_corrupt_inputs() -> None:
    candidate, request, _artwork_png, _artwork_json, metadata_json = _source_fixture()
    try:
        clean = _invoke(request, TEST_ROOT / "clean.json")
        assert clean.returncode == 0
        assert json.loads(clean.stdout)["state"] == "NOT_REQUIRED"

        malformed = dict(request)
        malformed["schema_version"] = "1"
        result = _invoke(malformed, TEST_ROOT / "malformed.json")
        assert result.returncode != 0
        assert json.loads(result.stdout)["state"] == "ERROR"

        metadata_path = candidate / "metadata.json"
        metadata_path.write_text('{"corrupted":true}', encoding="utf-8")
        corrupted = _invoke(request, TEST_ROOT / "corrupted.json")
        assert corrupted.returncode != 0
        assert json.loads(corrupted.stdout)["state"] == "ERROR"
        metadata_path.write_bytes(metadata_json)
    finally:
        shutil.rmtree(TEST_ROOT, ignore_errors=True)


def test_committed_real_godot_revalidation_integration_passes() -> None:
    source = INTEGRATION.read_text(encoding="utf-8")
    for marker in (
        'second_result.get("state") in ["STRUCTURAL ACCEPT", "STRUCTURAL REJECT"]',
        'second_result.get("working_grid_hash", "")) != first_working_hash',
        'second_stale.get("state") == "STALE"',
        'third_result.get("state") in ["STRUCTURAL ACCEPT", "STRUCTURAL REJECT"]',
        'revalidate_button != null and not revalidate_button.disabled',
        'reset.get("state") == "NOT_REQUIRED"',
    ):
        assert marker in source
    result = subprocess.run(
        ["godot", "--headless", "--path", "level_factory", "--script", "res://tests/factory_studio_art_revalidation_integration_suite.gd"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "SB-LF06-008-C001 manual artwork structural revalidation integration PASS" in output
