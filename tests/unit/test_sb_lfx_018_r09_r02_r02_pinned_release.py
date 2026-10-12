from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys
from unittest.mock import patch

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RELEASE_ROOT = REPOSITORY_ROOT / "Release" / "ScrubBots Factory Studio"
INSTALLED_SOURCE = RELEASE_ROOT / "src"
SOURCE_MODULES = INSTALLED_SOURCE if os.environ.get("LFX_R09_R02_R02_INSTALLED_TEST") == "1" else REPOSITORY_ROOT / "src"
if str(SOURCE_MODULES) not in sys.path:
    sys.path.insert(0, str(SOURCE_MODULES))

from scrubbots_pixel_factory import studio_extensions
from scrubbots_pixel_factory.supply_pipeline import pinned_game_source
from scrubbots_pixel_factory.supply_pipeline.game_rules import GameRules


PINNED_SOURCE_ID = "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
EXPECTED_SOURCE_SHA = "49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"
EXPECTED_RECORD_SHA = "858d302c10281ab2d70d4a9e22043e4eac216ebc6b6b0d89131b6e5930c232bb"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_dir(source_id: str) -> Path:
    return RELEASE_ROOT / "level_factory" / "output" / "owner-uploads" / source_id


def _png_size(path: Path) -> tuple[int, int]:
    raw = path.read_bytes()
    assert raw[:8] == b"\x89PNG\r\n\x1a\n"
    return int.from_bytes(raw[16:20], "big"), int.from_bytes(raw[20:24], "big")


def test_installed_release_pin_and_002_source_preflight_are_read_only() -> None:
    root = pinned_game_source.expected_runtime_root()
    assert root == pinned_game_source.repository_root() / "level_factory" / "output" / "current-game-runtime" / pinned_game_source.PINNED_MAIN_SHA
    manifest = pinned_game_source.verify_attested_runtime(root)
    assert len(manifest["source_files"]) == 232
    assert sum(entry["bytes"] for entry in manifest["source_files"]) == 1_977_597
    assert manifest["source_commit"] == "aef60a616d4ac401e9dfac15df6fe56e671c0053"

    source_png = _source_dir(PINNED_SOURCE_ID) / "source.png"
    source_record = _source_dir(PINNED_SOURCE_ID) / "source.json"
    before = (_sha(source_png), _sha(source_record))
    assert before == (EXPECTED_SOURCE_SHA, EXPECTED_RECORD_SHA)

    result = studio_extensions.validate_owner_source(
        PINNED_SOURCE_ID,
        persist=False,
        game_project=root,
        source_directory=_source_dir(PINNED_SOURCE_ID),
    )
    assert result["source_sha256"] == EXPECTED_SOURCE_SHA
    assert result["exact_logical_source"] is True
    assert result["original_dimensions"] == {"width": 32, "height": 32}
    assert result["palette"]["used_color_count"] == 7
    assert result["palette"]["foreign_color_count"] == 0
    assert result["alpha"] == {"transparent_count": 288, "semi_alpha_count": 0, "opaque_count": 736}
    assert result["void_capability"]["state"] == "OPEN"
    assert result["void_capability"]["runtime_kind"] == "LF_PINNED_SOURCE_MINIMAL_RUNTIME"
    assert result["structural"]["disposition"] == "PASS"
    assert "evidence_path" not in result
    for columns in (3, 4, 5):
        rules = GameRules(project=root, column_count=columns)
        assert rules.column_count == columns
        assert rules.attestation["source_commit"] == pinned_game_source.PINNED_MAIN_SHA
    assert (_sha(source_png), _sha(source_record)) == before


def test_pinned_runtime_cannot_authorize_a_different_owner_upload() -> None:
    root = pinned_game_source.expected_runtime_root()
    pinned_game_source.verify_attested_runtime(root)
    owner_root = RELEASE_ROOT / "level_factory" / "output" / "owner-uploads"
    other_id = next(
        directory.name
        for directory in sorted(owner_root.iterdir())
        if directory.is_dir() and directory.name.startswith("owner-upload-") and directory.name != PINNED_SOURCE_ID
    )
    result = studio_extensions.validate_owner_source(
        other_id,
        persist=False,
        game_project=root,
        source_directory=owner_root / other_id,
    )
    assert result["void_capability"]["state"] == "CLOSED"
    assert result["void_capability"]["reason_code"] == "PINNED_SOURCE_SCOPE_NOT_VERIFIED"
    assert result["exact_logical_source"] is False
    assert result["claims"]["solver"].startswith("NOT AVAILABLE")


def test_installed_gameplay_catalog_filters_by_content_dimensions_without_mutation() -> None:
    root = RELEASE_ROOT / "level_factory" / "output" / "owner-uploads"
    sources = sorted(path for path in root.iterdir() if path.is_dir() and path.name.startswith("owner-upload-"))
    before = {path.name: (_sha(path / "source.png"), _sha(path / "source.json")) for path in sources}
    eligible = []
    for directory in sources:
        width, height = _png_size(directory / "source.png")
        if 20 <= width <= 59 and 20 <= height <= 59:
            eligible.append(directory.name)
    assert len(sources) == 12
    assert len(eligible) == 9
    assert (_sha(_source_dir(PINNED_SOURCE_ID) / "source.png"), _sha(_source_dir(PINNED_SOURCE_ID) / "source.json")) == before[PINNED_SOURCE_ID]
    assert {path.name for path in sources} == set(before)


def test_pinned_file_manifest_and_release_root_fail_closed_when_tampered_or_stale(monkeypatch: pytest.MonkeyPatch) -> None:
    root = pinned_game_source.expected_runtime_root()
    manifest_path = root / "source-attestation.json"
    original_read_bytes = Path.read_bytes

    def read_tampered_manifest(path: Path) -> bytes:
        raw = original_read_bytes(path)
        return raw + b" " if path.resolve() == manifest_path.resolve() else raw

    with monkeypatch.context() as scoped:
        scoped.setattr(Path, "read_bytes", read_tampered_manifest)
        with pytest.raises(pinned_game_source.PinnedGameSourceError, match="attestation digest mismatch"):
            pinned_game_source.verify_attested_runtime(root)

    manifest = pinned_game_source.verify_attested_runtime(root)
    first_source = root / manifest["source_files"][0]["path"]
    original_is_file = Path.is_file

    def report_missing_source(path: Path) -> bool:
        if path.resolve() == first_source.resolve():
            return False
        return original_is_file(path)

    with monkeypatch.context() as scoped:
        scoped.setattr(Path, "is_file", report_missing_source)
        with pytest.raises(pinned_game_source.PinnedGameSourceError, match="missing or redirected"):
            pinned_game_source.verify_attested_runtime(root)

    with monkeypatch.context() as scoped:
        scoped.setattr(pinned_game_source, "expected_runtime_root", lambda: root.parent)
        with pytest.raises(pinned_game_source.PinnedGameSourceError, match="path is not"):
            pinned_game_source.verify_attested_runtime(root)
