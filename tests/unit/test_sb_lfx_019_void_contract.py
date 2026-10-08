from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from PIL import Image
import pytest

from scrubbots_pixel_factory.contracts import CANONICAL_PALETTE, count_used_colors
from scrubbots_pixel_factory.contracts.palette import VOID_CELL_ID
from scrubbots_pixel_factory.output.png import PNGContractError, decode_logical_png, encode_logical_png
from scrubbots_pixel_factory.quality import logical_grid_hash
from scrubbots_pixel_factory.supply_pipeline.game_rules import GameRules
from scrubbots_pixel_factory.supply_pipeline.pixel_analyzer import PixelAnalyzer
from scrubbots_pixel_factory.supply_pipeline.screening import ScreeningSimulator
from scrubbots_pixel_factory.supply_pipeline.supply_exporter import SupplyExporter
from scrubbots_pixel_factory.owner_upload import import_owner_upload
from scrubbots_pixel_factory import owner_upload, studio_extensions as studio
from scrubbots_pixel_factory.supply_pipeline import void_capability as void_module
from scrubbots_pixel_factory.supply_pipeline.game_publisher import PublicationError, publish_level
from scrubbots_pixel_factory.supply_pipeline.scrubpack_identity import derive_solver_supply_identity

CONTENT_PIPELINE = Path(__file__).resolve().parents[2] / "content_pipeline"
sys.path.insert(0, str(CONTENT_PIPELINE / "src"))
from scrubbots_content_pipeline import ScrubpackLevelInput, ScrubpackPayloadInput, ScrubpackSolverIdentityError, ScrubpackSolverProof  # noqa: E402
from scrubbots_content_pipeline.scrubpack_solver_identity import _proof_for_level  # noqa: E402


def _rgba(width: int, height: int, void_count: int = 550) -> bytes:
    pixels = bytearray()
    colors = ("C01", "C02", "C03")
    for index in range(width * height):
        if index < void_count:
            pixels.extend((0, 0, 0, 0))
        else:
            color = CANONICAL_PALETTE.rgb_for(colors[(index - void_count) % len(colors)])
            pixels.extend((*color, 255))
    return bytes(pixels)


def _png(width: int, height: int, pixels: bytes) -> bytes:
    image = Image.frombytes("RGBA", (width, height), pixels)
    from io import BytesIO

    output = BytesIO()
    image.save(output, format="PNG", optimize=False)
    return output.getvalue()


def _logical_rgba(width: int, height: int, artwork_count: int) -> bytes:
    pixels = bytearray(width * height * 4)
    for index in range(artwork_count):
        x = index % width
        color_id = ("C01", "C02", "C03")[min(2, x * 3 // width)]
        offset = index * 4
        pixels[offset : offset + 4] = bytes((*CANONICAL_PALETTE.rgb_for(color_id), 255))
    return bytes(pixels)


def _configure_upload_roots(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    repository = tmp_path / "factory"
    uploads = repository / "level_factory" / "output" / "owner-uploads"
    evidence = repository / "level_factory" / "output" / "studio-extensions"
    uploads.mkdir(parents=True)
    evidence.mkdir(parents=True)
    monkeypatch.setattr(owner_upload, "owner_upload_root", lambda: uploads)
    monkeypatch.setattr(owner_upload, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "owner_upload_root", lambda: uploads)
    monkeypatch.setattr(studio, "_repository_root", lambda: repository)
    monkeypatch.setattr(studio, "extensions_root", lambda: evidence)
    return repository, uploads


def test_void_png_roundtrip_preserves_opaque_legacy_encoding_and_hashes() -> None:
    opaque = ("C01", "C02", "C03", "C01")
    legacy = encode_logical_png(2, 2, opaque)
    assert hashlib.sha256(legacy).hexdigest() == "28afcf4966edca97429fb088c4001c38589d424754a9cfa03de618b1d7c8840d"
    assert decode_logical_png(legacy).cells == opaque

    cells = ("VOID", "C01", "C02", "C03")
    png = encode_logical_png(2, 2, cells)
    decoded = decode_logical_png(png)
    assert decoded.cells == cells
    assert decoded.palette == ("C01", "C02", "C03")
    assert decoded.raw_rgb == b"\0\0\0" + b"".join(bytes(CANONICAL_PALETTE.rgb_for(cell)) for cell in cells[1:])
    assert logical_grid_hash(2, 2, cells) != logical_grid_hash(2, 2, ("C01", "VOID", "C02", "C03"))


def test_alpha_and_color_counts_ignore_void_and_keep_source_bytes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repository, uploads = _configure_upload_roots(tmp_path, monkeypatch)
    monkeypatch.setattr(void_module, "void_capability", lambda _project=None: {"state": "OPEN", "disposition": "READY", "git_head": "a" * 40})

    source = tmp_path / "owner-32x32.png"
    source_bytes = _png(32, 32, _rgba(32, 32))
    source.write_bytes(source_bytes)
    imported = import_owner_upload(source)
    source_id = str(imported["source_id"])
    report = studio.validate_owner_source(source_id, persist=False, game_project=tmp_path / "current-game")

    assert report["alpha"] == {"transparent_count": 550, "semi_alpha_count": 0, "opaque_count": 474}
    assert report["artwork"] == {
        "cell_count": 474,
        "void_cell_count": 550,
        "minimum_rule": ">=200 non-VOID and >=25% W*H",
        "minimum_rule_pass": True,
    }
    assert report["palette"]["used_color_count"] == 3
    assert report["palette"]["used_color_count"] == count_used_colors([VOID_CELL_ID, "C01", "C02", "C03"])
    assert report["exact_logical_source"] is True
    assert (uploads / source_id / "source.png").read_bytes() == source_bytes


def test_gate_closed_transparent_owner_upload_has_reason_and_no_candidate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repository, uploads = _configure_upload_roots(tmp_path, monkeypatch)
    monkeypatch.setattr(void_module, "void_capability", lambda _project=None: {"state": "CLOSED", "disposition": "UNAVAILABLE", "reason": "fixture: current game authority not configured"})

    source = tmp_path / "transparent.png"
    source.write_bytes(_png(32, 32, _rgba(32, 32)))
    imported = import_owner_upload(source)
    source_id = str(imported["source_id"])
    result = studio.run_pipeline(source_id=source_id, request={"game_project": str(tmp_path / "current-game")})

    assert result["disposition"] == "UNAVAILABLE"
    assert "current game authority not configured" in json.dumps(result)
    assert not (repository / "level_factory" / "output" / "studio-derived-candidates").exists()
    assert not (repository / "level_factory" / "output" / "canonical-supply").exists()


def test_screening_void_border_connectivity_and_sealed_hole() -> None:
    ring = [[-1] * 5 for _ in range(5)]
    for y in range(1, 4):
        for x in range(1, 4):
            ring[y][x] = 0
    sim = ScreeningSimulator(ring)
    initial = sim.initial([[(0, 9)]])
    assert initial["left"] == 9
    assert initial["open"][0] == 1
    assert initial["open"][2 * 5 + 2] == 0

    corridor = [row[:] for row in ring]
    corridor[2][2] = -1
    # Border-connected VOID is open and does not contribute to active artwork.
    corridor[0][2] = -1
    corridor[1][2] = -1
    opened = ScreeningSimulator(corridor).initial([[(0, 8)]])
    assert opened["left"] == 7
    assert opened["open"][2 * 5 + 2] == 1


def test_export_gate_closes_before_creating_any_partial_output(tmp_path: Path) -> None:
    class ClosedRules:
        column_count = 3
        preview_depth = 3

        @staticmethod
        def void_capability() -> dict[str, str]:
            return {"state": "CLOSED", "reason": "fixture current-game gate closed"}

    result = {"_level": {"cells": [-1, 0], "palette": ["#FF4500"], "width": 2, "height": 1}, "export_notes": []}
    output = tmp_path / "must-not-exist"
    with pytest.raises(ValueError, match="TRANSPARENT_UNAVAILABLE"):
        SupplyExporter(ClosedRules()).export(result, output, "void_fixture")
    assert not output.exists()


def test_game_rules_never_falls_back_to_desktop_project(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SCRUBBOTS_PROJECT", raising=False)
    with pytest.raises(FileNotFoundError, match="implicit Desktop fallback is disabled"):
        GameRules()


def test_semi_alpha_is_rejected_by_png_decoder() -> None:
    with pytest.raises(PNGContractError, match="alpha must be binary"):
        decode_logical_png(_png(1, 1, bytes((1, 2, 3, 128))))


def test_void_minimum_200_and_larger_board_quarter_boundary(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _repository, _uploads = _configure_upload_roots(tmp_path, monkeypatch)
    monkeypatch.setattr(void_module, "void_capability", lambda _project=None: {"state": "OPEN", "disposition": "READY", "git_head": "a" * 40})

    cases = ((20, 20, 199, False), (20, 20, 200, True), (40, 20, 199, False), (40, 20, 200, True))
    for width, height, artwork_count, accepted in cases:
        source = tmp_path / f"boundary-{width}x{height}-{artwork_count}.png"
        source.write_bytes(_png(width, height, _logical_rgba(width, height, artwork_count)))
        imported = import_owner_upload(source)
        report = studio.validate_owner_source(str(imported["source_id"]), persist=False, game_project=tmp_path / "current-game")
        assert report["artwork"]["cell_count"] == artwork_count
        assert report["artwork"]["minimum_rule_pass"] is accepted
        assert (report["structural"]["disposition"] == "PASS") is accepted
        if accepted:
            assert report["exact_logical_source"] is True
        else:
            assert "MINIMUM_ARTWORK" in report["structural"]["rejection_codes"]


def test_all_void_owner_art_is_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _repository, _uploads = _configure_upload_roots(tmp_path, monkeypatch)
    monkeypatch.setattr(void_module, "void_capability", lambda _project=None: {"state": "OPEN", "disposition": "READY", "git_head": "a" * 40})
    source = tmp_path / "all-void.png"
    source.write_bytes(_png(20, 20, bytes(20 * 20 * 4)))
    imported = import_owner_upload(source)
    report = studio.validate_owner_source(str(imported["source_id"]), persist=False, game_project=tmp_path / "current-game")
    assert report["artwork"]["cell_count"] == 0
    assert report["artwork"]["void_cell_count"] == 400
    assert report["artwork"]["minimum_rule_pass"] is False
    assert report["exact_logical_source"] is False
    assert report["structural"]["disposition"] == "FAIL"


def test_opaque_v1_solver_identity_keeps_legacy_shape_and_void_layout_is_bound() -> None:
    authority = {"repository": "Sekiph82/Scrubbots", "branch": "main", "git_head": "a" * 40}
    result = {
        "solver_status": "SOLVED", "solution_final": "WIN",
        "solution_replay": {"ok": True, "solved": True, "finalActive": 0},
        "color_conservation_verification": {"all_ok": True},
        "solver_metrics": {"official_difficulty_v1": {"ok": True}},
    }
    plan = {
        "schema": "scrubbots.level_supply_plan.v1", "version": 1, "levelId": "identity-fixture",
        "columnCount": 3, "visiblePreviewDepth": 3, "maxRobotsPerBatch": 2,
        "columns": [
            [{"batchId": "b1", "cid": "C01", "robots": 1}],
            [{"batchId": "b2", "cid": "C02", "robots": 1}],
            [{"batchId": "b3", "cid": "C03", "robots": 1}],
        ],
    }
    opaque_level = {"version": 1, "id": "identity-fixture", "width": 3, "height": 1, "palette": ["#FF4500FF", "#00A8E8FF", "#7AC943FF"], "cells": [0, 1, 2]}
    level_bytes = json.dumps(opaque_level, separators=(",", ":")).encode()
    plan_bytes = json.dumps(plan, separators=(",", ":")).encode()
    opaque_identity = derive_solver_supply_identity(level_bytes, plan_bytes, result, authority)
    assert "artwork_cell_count" not in opaque_identity
    assert "void_cell_count" not in opaque_identity

    void_level = {**opaque_level, "version": 2, "width": 4, "cells": [0, 1, 2, -1]}
    void_level_bytes = json.dumps(void_level, separators=(",", ":")).encode()
    void_identity = derive_solver_supply_identity(void_level_bytes, plan_bytes, result, authority)
    assert void_identity["artwork_cell_count"] == 3
    assert void_identity["void_cell_count"] == 1
    moved_void = {**void_level, "cells": [0, -1, 1, 2]}
    moved_identity = derive_solver_supply_identity(json.dumps(moved_void, separators=(",", ":")).encode(), plan_bytes, result, authority)
    assert moved_identity["solver_state_sha256"] != void_identity["solver_state_sha256"]


def test_scrubpack_rejects_wrong_v2_artwork_and_void_identity_counts(tmp_path: Path) -> None:
    authority = {"repository": "Sekiph82/Scrubbots", "branch": "main", "git_head": "a" * 40}
    level_id = "void-count-binding"
    level = {"version": 2, "id": level_id, "width": 4, "height": 1, "palette": ["#FF4500FF", "#00A8E8FF", "#7AC943FF"], "cells": [0, 1, 2, -1]}
    plan = {
        "schema": "scrubbots.level_supply_plan.v1", "version": 1, "levelId": level_id,
        "columnCount": 3, "visiblePreviewDepth": 3, "maxRobotsPerBatch": 1,
        "columns": [
            [{"batchId": "b1", "cid": "C01", "robots": 1}],
            [{"batchId": "b2", "cid": "C02", "robots": 1}],
            [{"batchId": "b3", "cid": "C03", "robots": 1}],
        ],
    }
    level_bytes = json.dumps(level, separators=(",", ":")).encode()
    plan_bytes = json.dumps(plan, separators=(",", ":")).encode()
    result = {
        "solver_status": "SOLVED", "solution_final": "WIN",
        "solution_replay": {"ok": True, "solved": True, "finalActive": 0},
        "solution_trace": [], "color_conservation_verification": {"all_ok": True},
        "solver_metrics": {"official_difficulty_v1": {"ok": True}},
    }
    identity = derive_solver_supply_identity(level_bytes, plan_bytes, result, authority)
    result["solver_supply_identity"] = identity
    level_path, plan_path = tmp_path / "level.json", tmp_path / "plan.json"
    level_path.write_bytes(level_bytes)
    plan_path.write_bytes(plan_bytes)
    primary = {
        "state": "READY", "disposition": "READY", "authority": authority,
        "result": result, "solver_supply_identity": identity,
        "files": {"level": str(level_path), "supply_plan": str(plan_path)},
        "load_check": {"state": "READY"},
    }
    pipeline = {
        "schema": "scrubbots-studio-pipeline-run", "version": 2, "disposition": "READY",
        "run_id": "pipeline-void-count-binding", "candidate_id": "void-count-binding",
        "stages": [{"stage": stage, "disposition": "PASS"} for stage in ("SOLVE", "REPLAY", "QA")],
        "primary": primary,
    }
    pipeline_bytes = json.dumps(pipeline, sort_keys=True, separators=(",", ":")).encode()
    proof_entry = {
        "schema": "scrubbots.factory.accepted-ready-proof/v1", "candidate_id": "void-count-binding",
        "pipeline_run_id": pipeline["run_id"], "pipeline_sha256": hashlib.sha256(pipeline_bytes).hexdigest(),
        "review_id": "review-void-count-binding-1",
    }
    fixture = ScrubpackLevelInput(
        level_id,
        ScrubpackPayloadInput({}, level_bytes),
        ScrubpackPayloadInput({}, plan_bytes),
        ScrubpackPayloadInput({}, b"{}"),
    )
    assert _proof_for_level(fixture, ScrubpackSolverProof(pipeline_bytes, proof_entry))["void_cell_count"] == 1

    wrong_identity = {**identity, "void_cell_count": 2}
    pipeline["primary"]["solver_supply_identity"] = wrong_identity
    pipeline["primary"]["result"]["solver_supply_identity"] = wrong_identity
    wrong_bytes = json.dumps(pipeline, sort_keys=True, separators=(",", ":")).encode()
    wrong_entry = {**proof_entry, "pipeline_sha256": hashlib.sha256(wrong_bytes).hexdigest()}
    with pytest.raises(ScrubpackSolverIdentityError, match="counts differ from exact packaged LevelData"):
        _proof_for_level(fixture, ScrubpackSolverProof(wrong_bytes, wrong_entry))


def test_transparent_publisher_is_capability_gated_and_does_not_write(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    game = tmp_path / "game"
    (game / "data/config").mkdir(parents=True)
    (game / "data/levels/catalog").mkdir(parents=True)
    (game / "project.godot").write_text("", encoding="utf-8")
    (game / "data/config/level_progression_v1.json").write_text("{}", encoding="utf-8")
    catalog = game / "data/levels/catalog/production_catalog_v1.json"
    catalog_bytes = b'{"schema":"scrubbots.production_catalog.v1","entries":[]}'
    catalog.write_bytes(catalog_bytes)
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "artwork.png").write_bytes(b"fixture")
    level_path, plan_path = tmp_path / "level.json", tmp_path / "plan.json"
    level_path.write_text(json.dumps({"version": 2, "id": "void-gated", "cells": [-1, 0, 1]}), encoding="utf-8")
    plan_path.write_text(json.dumps({"schema": "scrubbots.level_supply_plan.v1", "levelId": "void-gated", "columnCount": 3, "visiblePreviewDepth": 3, "maxRobotsPerBatch": 1, "columns": []}), encoding="utf-8")
    monkeypatch.setattr(void_module, "void_capability", lambda _project=None: {"state": "CLOSED", "disposition": "UNAVAILABLE", "reason": "fixture gate closed"})
    with pytest.raises(PublicationError, match="TRANSPARENT_UNAVAILABLE"):
        publish_level(
            game_project=game,
            candidate={"candidate_id": "void-gated", "background_intent": "TRANSPARENT", "artwork_sha256": "a" * 64},
            pipeline={"disposition": "READY", "primary": {"state": "READY", "load_check": {"state": "READY", "disposition": "READY"}, "files": {"level": str(level_path), "supply_plan": str(plan_path)}}},
            source_bundle=bundle,
            level_number=1,
        )
    assert catalog.read_bytes() == catalog_bytes
    assert not (game / "data/levels/void-gated.json").exists()
