from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scrubbots_pixel_factory import studio_extensions
from scrubbots_pixel_factory.supply_pipeline import pinned_game_source
from scrubbots_pixel_factory.supply_pipeline.game_publisher import PublicationError, discover_game_project
from scrubbots_pixel_factory.supply_pipeline.scrubbots_solver import ScrubBotsSolver
from scrubbots_pixel_factory.supply_pipeline.void_capability import void_capability


SOURCE_ID = "owner-upload-49667ba3a1018b4b6739ce42a9644eca291390970b2e251adda72a1c3c90e8aa"


def _owner_release_source() -> Path:
    return (
        pinned_game_source.repository_root()
        / "Release"
        / "ScrubBots Factory Studio"
        / "level_factory"
        / "output"
        / "owner-uploads"
        / SOURCE_ID
    )


def test_pinned_runtime_is_hash_bound_and_not_full_game_or_publish_authority() -> None:
    runtime = pinned_game_source.expected_runtime_root()
    manifest = pinned_game_source.verify_attested_runtime(runtime)
    assert manifest["source_commit"] == pinned_game_source.PINNED_MAIN_SHA
    assert manifest["source_files_count"] == 232
    assert manifest["source_files_bytes"] == 1_977_597
    assert manifest["full_game_checkout_verified"] is False

    gate = void_capability(runtime)
    assert gate["state"] == "OPEN"
    assert gate["runtime_kind"] == pinned_game_source.RUNTIME_KIND
    assert gate["full_game_checkout_verified"] is False
    with pytest.raises(PublicationError, match="CPX-002"):
        discover_game_project(runtime)


def test_attestation_rejects_modified_git_blob(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = pinned_game_source.expected_runtime_root()
    copy = tmp_path / pinned_game_source.PINNED_MAIN_SHA
    copy.mkdir()
    manifest_raw = (runtime / "source-attestation.json").read_bytes()
    entries = json.loads(manifest_raw)["source_files"]
    for entry in entries:
        source = runtime / entry["path"]
        destination = copy / entry["path"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(source.read_bytes())
    (copy / "source-attestation.json").write_bytes(manifest_raw)
    (copy / "project.godot").write_bytes((runtime / "project.godot").read_bytes())
    monkeypatch.setattr(pinned_game_source, "expected_runtime_root", lambda: copy)
    entry = json.loads((copy / "source-attestation.json").read_text(encoding="utf-8"))["source_files"][0]
    source = copy / entry["path"]
    source.write_bytes(source.read_bytes() + b"# altered\n")
    with pytest.raises(pinned_game_source.PinnedGameSourceError, match="mismatch"):
        pinned_game_source.verify_attested_runtime(copy)


def test_release_owner_source_root_is_read_only_and_preserves_same_identity() -> None:
    source_dir = _owner_release_source()
    png = source_dir / "source.png"
    record = source_dir / "source.json"
    before = (hashlib.sha256(png.read_bytes()).hexdigest(), hashlib.sha256(record.read_bytes()).hexdigest())
    verified = studio_extensions.verify_owner_source(SOURCE_ID, source_directory=source_dir)
    assert verified["source_sha256"] == before[0]
    assert Path(verified["source_path"]).resolve() == png.resolve()

    validation = studio_extensions.validate_owner_source(
        SOURCE_ID,
        persist=False,
        game_project=pinned_game_source.expected_runtime_root(),
        source_directory=source_dir,
    )
    assert validation["exact_logical_source"] is True
    assert validation["structural"]["disposition"] == "PASS"
    assert validation["alpha"] == {"transparent_count": 288, "semi_alpha_count": 0, "opaque_count": 736}
    assert validation["palette"]["foreign_color_count"] == 0
    after = (hashlib.sha256(png.read_bytes()).hexdigest(), hashlib.sha256(record.read_bytes()).hexdigest())
    assert after == before


def test_derived_candidate_lineage_points_to_external_release_source_record() -> None:
    source_dir = _owner_release_source()
    assert studio_extensions._owner_source_record_reference(source_dir / "source.png") == (
        source_dir / "source.json"
    ).resolve().relative_to(pinned_game_source.repository_root().resolve()).as_posix()


def test_attested_solver_timeout_terminates_and_keeps_jobs_in_project_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class FakeProcess:
        def __init__(self, _args, **kwargs):
            self.returncode = None
            self.stdout = io.StringIO("fake godot started\n")
            self.kwargs = kwargs
            self.terminated = False

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

        def poll(self):
            return self.returncode

        def terminate(self):
            self.terminated = True
            self.returncode = 1

        def wait(self, timeout=None):
            return self.returncode

        def kill(self):
            self.returncode = -9

    captured: dict[str, FakeProcess] = {}

    def fake_popen(args, **kwargs):
        process = FakeProcess(args, **kwargs)
        captured["process"] = process
        return process

    monkeypatch.setattr("scrubbots_pixel_factory.supply_pipeline.scrubbots_solver.subprocess.Popen", fake_popen)
    rules = SimpleNamespace(
        project=tmp_path,
        attestation={"source_commit": pinned_game_source.PINNED_MAIN_SHA},
        palette=[],
        preview_depth=3,
        column_count=3,
        authority={},
    )
    solver = ScrubBotsSolver(rules, godot="fake-godot")
    level = {"id": "bounded", "width": 1, "height": 1, "palette": ["#000000FF"], "cells": [0]}
    with pytest.raises(RuntimeError, match="timed out"):
        solver.run(level, [], timeout=0.1)
    assert captured["process"].terminated is True
    temp_env = captured["process"].kwargs["env"]
    assert temp_env["TEMP"].startswith(str(tmp_path))
    assert (tmp_path / ".lf_solver_jobs").is_dir()
