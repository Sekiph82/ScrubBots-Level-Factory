from __future__ import annotations

import json
from pathlib import Path

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


def test_void_png_roundtrip_preserves_opaque_legacy_encoding_and_hashes() -> None:
    opaque = ("C01", "C02", "C03", "C01")
    legacy = encode_logical_png(2, 2, opaque)
    assert decode_logical_png(legacy).cells == opaque

    cells = ("VOID", "C01", "C02", "C03")
    png = encode_logical_png(2, 2, cells)
    decoded = decode_logical_png(png)
    assert decoded.cells == cells
    assert decoded.palette == ("C01", "C02", "C03")
    assert decoded.raw_rgb == b"\0\0\0" + b"".join(bytes(CANONICAL_PALETTE.rgb_for(cell)) for cell in cells[1:])
    assert logical_grid_hash(2, 2, cells) != logical_grid_hash(2, 2, ("C01", "VOID", "C02", "C03"))


def test_alpha_and_color_counts_ignore_void_and_keep_source_bytes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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
    assert report["palette"]["used_color_count"] == count_used_colors([VOID_CELL_ID, "C01", "C02", "C03"])
    assert report["exact_logical_source"] is True
    assert (uploads / source_id / "source.png").read_bytes() == source_bytes


def test_gate_closed_transparent_owner_upload_has_reason_and_no_candidate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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
    monkeypatch.setattr(void_module, "void_capability", lambda _project=None: {"state": "CLOSED", "disposition": "UNAVAILABLE", "reason": "fixture: current game authority not configured"})

    source = tmp_path / "transparent.png"
    source.write_bytes(_png(32, 32, _rgba(32, 32)))
    imported = import_owner_upload(source)
    source_id = str(imported["source_id"])
    result = studio.run_pipeline(source_id=source_id, request={"game_project": str(tmp_path / "current-game")})

    assert result["disposition"] == "UNAVAILABLE"
    assert "current game authority not configured" in json.dumps(result)
    assert not (repository / "level_factory" / "output" / "studio-derived-candidates").exists()


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
