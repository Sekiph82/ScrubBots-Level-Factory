from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

import pytest

from scrubbots_pixel_factory import studio_extensions
from scrubbots_pixel_factory.supply_pipeline import real_play_gate, release_pool


FAKE_GODOT_CMD = r"""@echo off
if "%~1"=="--version" (
  echo %REAL_PLAY_STUB_VERSION%
  exit /b 0
)
set /p STEP=<"%REAL_PLAY_STUB_COUNTER%"
set /a STEP+=1
> "%REAL_PLAY_STUB_COUNTER%" echo %STEP%
>> "%REAL_PLAY_STUB_ARGS_LOG%" echo %*
if "%STEP%"=="1" goto step1
if "%STEP%"=="2" goto step2
if "%STEP%"=="3" goto step3
exit /b 9
:step1
copy /Y "%REAL_PLAY_STUB_JSON_1%" "%REAL_PLAY_STUB_OUT_FILE%" >nul
type "%REAL_PLAY_STUB_STDOUT_1%"
exit /b %REAL_PLAY_STUB_EXIT_1%
:step2
copy /Y "%REAL_PLAY_STUB_JSON_2%" "%REAL_PLAY_STUB_OUT_FILE%" >nul
type "%REAL_PLAY_STUB_STDOUT_2%"
exit /b %REAL_PLAY_STUB_EXIT_2%
:step3
copy /Y "%REAL_PLAY_STUB_JSON_3%" "%REAL_PLAY_STUB_OUT_FILE%" >nul
type "%REAL_PLAY_STUB_STDOUT_3%"
exit /b %REAL_PLAY_STUB_EXIT_3%
"""


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _normalized_sha(path: Path) -> str:
    return _sha(path.read_bytes().replace(b"\r\n", b"\n"))


def _fixture(root: Path) -> dict[str, Path | dict[str, Any]]:
    factory = root / "factory"
    game = root / "game"
    run = factory / "level_factory" / "output" / "studio-extensions" / "canonical-supply" / "candidate-test" / "run-test"
    run.mkdir(parents=True)
    (game / "tools").mkdir(parents=True)
    (game / "project.godot").write_text("config_version=5\n", encoding="utf-8")
    (game / "tools" / "real_play_file.gd").write_text("# fake-game project fixture\n", encoding="utf-8")
    level = run / "candidate-test.json"
    plan = run / "candidate-test_supply_v1.json"
    level_value = {"id": "level_fake", "version": 1, "cells": [0, 1]}
    plan_value = {
        "levelId": "level_fake",
        "intendedColumnClicks": [1, 2, 3],
        "preservedMetadata": {"owner": "test-fixture", "sequence": ["a", "b"]},
    }
    level.write_text(json.dumps(level_value, sort_keys=True, indent=2) + "\r\n", encoding="utf-8")
    plan.write_text(json.dumps(plan_value, sort_keys=True, indent=2) + "\r\n", encoding="utf-8")
    return {"factory": factory, "game": game, "run": run, "level": level, "plan": plan, "level_value": level_value, "plan_value": plan_value}


def _result(
    fixture: dict[str, Path | dict[str, Any]],
    *,
    verdict: str = "WON_CANONICAL",
    exit_code: int = 0,
    searched: bool = False,
    plan_sha: str | None = None,
    level_sha: str | None = None,
    clicks: list[int] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    level = fixture["level"]
    plan = fixture["plan"]
    assert isinstance(level, Path) and isinstance(plan, Path)
    plan_value = json.loads(plan.read_text(encoding="utf-8"))
    result: dict[str, Any] = {
        "error": error,
        "exitCode": exit_code,
        "gameCommit": "a" * 40,
        "levelFile": str(level.resolve()) if verdict != "INVALID_INPUT" else None,
        "levelId": "level_fake" if verdict != "INVALID_INPUT" else None,
        "levelSha256": level_sha or _normalized_sha(level) if verdict != "INVALID_INPUT" else None,
        "model": "real_play_v1",
        "runId": "test-run-001",
        "timestamp": "2026-11-07T12:00:00Z",
        "sourceSha256": "d" * 64,
        "mode": "canonical_60hz",
        "canonicalDt": "1/60",
        "perDt": {
            "1/60": {
                "won": verdict == "WON_CANONICAL",
                "stuckClickIndex": 27 if verdict == "LOST" else None,
                "slots": [{"index": 0, "state": "WAITING"}] if verdict == "LOST" else None,
                "final": {
                    "supplyExhausted": verdict == "WON_CANONICAL",
                    "targetsCleared": verdict == "WON_CANONICAL",
                    "slotsEmpty": verdict == "WON_CANONICAL",
                    "activeRobots": 0 if verdict == "WON_CANONICAL" else 1,
                    "boardResidue": 0 if verdict == "WON_CANONICAL" else 1,
                },
            },
        } if verdict != "INVALID_INPUT" else {},
        "planClicks": list(clicks if clicks is not None else plan_value.get("intendedColumnClicks", [])) if verdict != "INVALID_INPUT" else [],
        "planFile": str(plan.resolve()) if verdict != "INVALID_INPUT" else None,
        "planSha256": plan_sha or _normalized_sha(plan) if verdict != "INVALID_INPUT" else None,
        "schema": "scrubbots.real_play_file_result.v2",
        "search": {"status": "SOLVED", "canonicalWin": True} if searched else None,
        "searched": searched,
        "searchedClicks": [3, 2, 1] if searched and verdict == "WON_CANONICAL" else None,
        "verdict": verdict,
    }
    return result


def _fake_cli(tmp_path: Path, fixture: dict[str, Path | dict[str, Any]], scenarios: list[tuple[str, int]], *, version: str = "4.7.2.stable.fake") -> tuple[Path, dict[str, str]]:
    script = tmp_path / "fake-godot.cmd"
    script.write_text(FAKE_GODOT_CMD, encoding="ascii")
    env = os.environ.copy()
    counter = tmp_path / "calls.txt"
    counter.write_text("0\n", encoding="ascii")
    args_log = tmp_path / "args.txt"
    env.update({
        "REAL_PLAY_STUB_VERSION": version,
        "REAL_PLAY_STUB_COUNTER": str(counter),
        "REAL_PLAY_STUB_ARGS_LOG": str(args_log),
        "REAL_PLAY_STUB_OUT_FILE": str(Path(fixture["run"]) / "real_play_result_v1.json"),
    })
    for index in range(1, 4):
        if index <= len(scenarios):
            stdout_text, exit_code = scenarios[index - 1]
        else:
            stdout_text, exit_code = "REAL_PLAY_RESULT {}\n", 0
        stdout_path = tmp_path / f"stdout-{index}.txt"
        json_path = tmp_path / f"json-{index}.json"
        stdout_path.write_text(stdout_text, encoding="utf-8")
        marker = stdout_text.split("REAL_PLAY_RESULT ", 1)[-1].strip()
        try:
            json_path.write_text(json.dumps(json.loads(marker)), encoding="utf-8")
        except json.JSONDecodeError:
            json_path.write_text("{}", encoding="utf-8")
        env[f"REAL_PLAY_STUB_STDOUT_{index}"] = str(stdout_path)
        env[f"REAL_PLAY_STUB_JSON_{index}"] = str(json_path)
        env[f"REAL_PLAY_STUB_EXIT_{index}"] = str(exit_code)
    settings = {
        "scrubbotsRepoPath": str(fixture["game"]),
        "godotExe": str(script),
        "realPlayTimeoutSeconds": 5,
    }
    return script, {**env, "_settings_json": json.dumps(settings)}


def _run_gate(fixture: dict[str, Path | dict[str, Any]], env: dict[str, str]) -> dict[str, Any]:
    settings = json.loads(env.pop("_settings_json"))
    return real_play_gate.ensure_real_play_gate(
        fixture["level"],
        fixture["plan"],
        Path(fixture["run"]) / "real_play_result_v1.json",
        settings=settings,
        studio_root=fixture["factory"],
        environ=env,
        source_sha256="d" * 64,
    )


def _stdout(result: dict[str, Any]) -> str:
    return "startup banner\nREAL_PLAY_RESULT " + json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n"


def test_fake_cli_canonical_win_is_accepted_and_stdout_out_match(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    result = _result(fixture)
    _script, env = _fake_cli(tmp_path, fixture, [(_stdout(result), 0)])
    evidence = _run_gate(fixture, env)
    assert evidence["result"]["verdict"] == "WON_CANONICAL"
    assert evidence["result"]["searched"] is False
    assert evidence["plan_sha256"] == _normalized_sha(Path(fixture["plan"]))
    assert Path(evidence["result_path"]).is_file()
    assert evidence["result_sha256"] == _sha(Path(evidence["result_path"]).read_bytes())
    args = (tmp_path / "args.txt").read_text(encoding="utf-8")
    assert "--level-file" in args and "--plan-file" in args and "--out" in args
    assert "--canonical-only" in args
    assert "--search" not in args


def test_new_factory_ready_requires_canonical_60hz_and_does_not_accept_legacy_robust() -> None:
    source_sha = "d" * 64
    canonical = {
        "schema": "scrubbots.real_play_file_result.v2",
        "mode": "canonical_60hz",
        "canonicalDt": "1/60",
        "verdict": "WON_CANONICAL",
        "searched": False,
        "sourceSha256": source_sha,
        "perDt": {"1/60": {"won": True, "final": {
            "supplyExhausted": True,
            "targetsCleared": True,
            "slotsEmpty": True,
            "activeRobots": 0,
            "boardResidue": 0,
        }}},
    }
    assert studio_extensions._require_canonical_ready_real_play(canonical, source_sha) is None
    boolean_count = json.loads(json.dumps(canonical))
    boolean_count["perDt"]["1/60"]["final"]["activeRobots"] = False
    with pytest.raises(studio_extensions.StudioExtensionError, match="complete WON_CANONICAL result"):
        studio_extensions._require_canonical_ready_real_play(boolean_count, source_sha)

    legacy_robust = {
        **canonical,
        "schema": "scrubbots.real_play_file_result.v1",
        "mode": None,
        "canonicalDt": None,
        "verdict": "WON_ROBUST",
        "perDt": {rate: {"won": True} for rate in ("1/30", "1/60", "1/120")},
    }
    with pytest.raises(studio_extensions.StudioExtensionError, match="complete WON_CANONICAL result"):
        studio_extensions._require_canonical_ready_real_play(legacy_robust, source_sha)


def test_searched_clicks_splice_only_the_array_and_require_no_search_replay(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    plan = Path(fixture["plan"])
    initial = _result(fixture, verdict="LOST", exit_code=1)
    searched = _result(fixture, searched=True)
    expected_plan = json.loads(plan.read_text(encoding="utf-8"))
    expected_plan["intendedColumnClicks"] = [3, 2, 1]
    rewritten_text = plan.read_bytes().decode("utf-8")
    rewritten_text = real_play_gate._CLICK_ARRAY.sub(r'\g<1>[3,2,1]', rewritten_text, count=1)
    new_plan_sha = hashlib.sha256(rewritten_text.encode("utf-8").replace(b"\r\n", b"\n")).hexdigest()
    final = _result(fixture, plan_sha=new_plan_sha, clicks=[3, 2, 1])
    _script, env = _fake_cli(tmp_path, fixture, [(_stdout(initial), 1), (_stdout(searched), 0), (_stdout(final), 0)])
    original = plan.read_text(encoding="utf-8")
    evidence = _run_gate(fixture, env)
    after = plan.read_text(encoding="utf-8")
    updated = json.loads(plan.read_text(encoding="utf-8"))
    assert updated["intendedColumnClicks"] == [3, 2, 1]
    assert {key: value for key, value in updated.items() if key != "intendedColumnClicks"} == {
        key: value for key, value in expected_plan.items() if key != "intendedColumnClicks"
    }
    original_match = real_play_gate._CLICK_ARRAY.search(original)
    after_match = real_play_gate._CLICK_ARRAY.search(after)
    assert original_match is not None and after_match is not None
    assert original[: original_match.start()] == after[: after_match.start()]
    assert original[original_match.end() :] == after[after_match.end() :]
    assert evidence["plan_sha256"] == new_plan_sha
    assert evidence["result"]["searched"] is False
    calls = (tmp_path / "args.txt").read_text(encoding="utf-8").splitlines()
    assert len(calls) == 3 and all("--canonical-only" in call for call in calls)
    assert "--search" not in calls[0] and "--search" in calls[1] and "--search" not in calls[2]


@pytest.mark.parametrize(
    ("verdict", "exit_code", "search_verdict", "expected"),
    [
        ("WON_CANONICAL_ONLY", 1, "WON_CANONICAL_ONLY", "WON_CANONICAL_ONLY"),
        ("LOST", 1, "LOST", "LOST: stuck after click 27; slot 0: WAITING"),
        ("LOST", 1, "SEARCH_EXHAUSTED", "SEARCH_EXHAUSTED"),
        ("LOST", 1, "SEARCH_BUDGET", "SEARCH_BUDGET"),
    ],
)
def test_non_robust_and_search_failures_never_accept(
    tmp_path: Path, verdict: str, exit_code: int, search_verdict: str, expected: str,
) -> None:
    fixture = _fixture(tmp_path)
    initial = _result(fixture, verdict=verdict, exit_code=exit_code)
    searched = _result(fixture, verdict=search_verdict, exit_code=1, searched=True)
    _script, env = _fake_cli(tmp_path, fixture, [(_stdout(initial), exit_code), (_stdout(searched), 1)])
    with pytest.raises(real_play_gate.RealPlayGateError, match=expected):
        _run_gate(fixture, env)


def test_invalid_input_is_rejected_with_game_error_detail(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    invalid = _result(fixture, verdict="INVALID_INPUT", exit_code=2, error="level id mismatch")
    _script, env = _fake_cli(tmp_path, fixture, [(_stdout(invalid), 2)])
    with pytest.raises(real_play_gate.RealPlayGateError, match="export bug: level id mismatch"):
        _run_gate(fixture, env)


@pytest.mark.parametrize(
    ("mutate", "process_exit", "message"),
    [
        (lambda result: result.update(schema="wrong"), 0, "wrong schema"),
        (lambda result: result.update(model="wrong"), 0, "wrong model"),
        (lambda result: result.update(exitCode=3), 0, "exitCode mismatch"),
        (lambda result: result.update(verdict="WON_ROBUST", exitCode=3), 3, "verdict/exit mismatch"),
        (lambda result: result.update(planSha256="0" * 64), 0, "planSha256 does not match"),
        (lambda result: result.update(levelSha256="0" * 64), 0, "levelSha256 does not match"),
        (lambda result: result.update(schema="scrubbots.real_play_file_result.v1"), 0, "canonical-only result contract"),
        (lambda result: result.update(canonicalDt="1/30"), 0, "canonical_60hz at 1/60"),
        (lambda result: result.update(sourceSha256="0" * 64), 0, "sourceSha256 does not match"),
        (lambda result: result["perDt"]["1/60"]["final"].update(slotsEmpty=False), 0, "complete 1/60 game-host WIN"),
        (lambda result: result["perDt"]["1/60"]["final"].update(activeRobots=False), 0, "complete 1/60 game-host WIN"),
        (lambda result: result["perDt"]["1/60"]["final"].update(boardResidue=False), 0, "complete 1/60 game-host WIN"),
    ],
)
def test_result_contract_mismatches_fail_closed(
    tmp_path: Path, mutate: Any, process_exit: int, message: str,
) -> None:
    fixture = _fixture(tmp_path)
    result = _result(fixture)
    mutate(result)
    _script, env = _fake_cli(tmp_path, fixture, [(_stdout(result), process_exit)])
    with pytest.raises(real_play_gate.RealPlayGateError, match=message):
        _run_gate(fixture, env)


def test_missing_marker_and_malformed_json_fail_closed(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    _script, env = _fake_cli(tmp_path, fixture, [("Godot banner only\n", 0)])
    with pytest.raises(real_play_gate.RealPlayGateError, match="no REAL_PLAY_RESULT"):
        _run_gate(fixture, env)

    fixture = _fixture(tmp_path / "malformed")
    _script, env = _fake_cli(tmp_path / "malformed", fixture, [("REAL_PLAY_RESULT {broken}\n", 0)])
    with pytest.raises(real_play_gate.RealPlayGateError, match="invalid JSON"):
        _run_gate(fixture, env)


def test_version_and_game_repository_preflight_fail_closed(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    _script, env = _fake_cli(tmp_path, fixture, [], version="4.6.9.stable.fake")
    with pytest.raises(real_play_gate.RealPlayGateError, match="expected version 4.7.2"):
        _run_gate(fixture, env)

    fixture = _fixture(tmp_path / "missing-tool")
    (Path(fixture["game"]) / "tools" / "real_play_file.gd").unlink()
    _script, env = _fake_cli(tmp_path / "missing-tool", fixture, [])
    with pytest.raises(real_play_gate.RealPlayGateError, match="scrubbotsRepoPath setting is invalid"):
        _run_gate(fixture, env)


def test_settings_resolve_ui_values_then_environment_then_defaults() -> None:
    default = real_play_gate.resolve_real_play_settings({}, {})
    assert default["scrubbotsRepoPath"] == str(real_play_gate.DEFAULT_SCRUBBOTS_REPO)
    assert default["godotExe"] == str(real_play_gate.DEFAULT_GODOT_EXE)
    assert default["realPlayTimeoutSeconds"] == real_play_gate.DEFAULT_TIMEOUT_SECONDS
    from_env = real_play_gate.resolve_real_play_settings(None, {"SCRUBBOTS_REPO": "X:/game", "GODOT": "X:/godot.exe"})
    assert from_env["scrubbotsRepoPath"] == "X:/game"
    assert from_env["godotExe"] == "X:/godot.exe"
    configured = real_play_gate.resolve_real_play_settings(
        {"scrubbotsRepoPath": "Y:/game", "godotExe": "Y:/godot.exe", "realPlayTimeoutSeconds": 30},
        {"SCRUBBOTS_REPO": "X:/game", "GODOT": "X:/godot.exe"},
    )
    assert configured == {"scrubbotsRepoPath": "Y:/game", "godotExe": "Y:/godot.exe", "realPlayTimeoutSeconds": 30}


def test_settings_dialog_exposes_real_play_settings_without_adding_a_screen() -> None:
    source = (Path(__file__).parents[2] / "level_factory" / "scripts" / "factory_studio_exact_ui.gd").read_text(encoding="utf-8")
    assert "scrubbotsRepoPath" in source
    assert "godotExe" in source
    assert "realPlayTimeoutSeconds" in source
    assert 'OS.set_environment("SCRUBBOTS_REPO"' in source
    assert 'OS.set_environment("GODOT"' in source
    assert 'OS.set_environment("SCRUBBOTS_REAL_PLAY_TIMEOUT_SECONDS"' in source


def test_runtime_timeout_fails_closed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    _script, env = _fake_cli(tmp_path, fixture, [])
    settings = json.loads(env.pop("_settings_json"))
    actual_run = real_play_gate.run_studio_child_interruptibly

    def timeout_after_version(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        if len(args) == 2 and args[1] == "--version":
            return actual_run(args, **kwargs)
        raise subprocess.TimeoutExpired(args, timeout=0.1)

    monkeypatch.setattr(real_play_gate, "run_studio_child_interruptibly", timeout_after_version)
    with pytest.raises(real_play_gate.RealPlayGateError, match="timed out after"):
        real_play_gate.ensure_real_play_gate(
            fixture["level"], fixture["plan"], Path(fixture["run"]) / "real_play_result_v1.json",
            settings=settings, studio_root=fixture["factory"], environ=env,
        )


def test_legacy_v1_robust_receipt_is_readable_but_not_current_release_acceptance(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    level = Path(fixture["level"])
    plan = Path(fixture["plan"])
    result_path = Path(fixture["run"]) / "real_play_result_v1.json"
    result = {
        "schema": "scrubbots.real_play_file_result.v1", "model": "real_play_v1",
        "verdict": "WON_ROBUST", "exitCode": 0,
        "perDt": {},
        "planClicks": json.loads(plan.read_text(encoding="utf-8"))["intendedColumnClicks"],
        "levelSha256": _normalized_sha(level), "planSha256": _normalized_sha(plan), "gameCommit": "a" * 40,
    }
    result_path.write_text(json.dumps(result), encoding="utf-8")
    files = {
        "level": {"path": str(level), "sha256": _sha(level.read_bytes())},
        "supply_plan": {"path": str(plan), "sha256": _sha(plan.read_bytes())},
        "real_play_result": {"path": str(result_path), "sha256": _sha(result_path.read_bytes())},
    }
    entry = {
        "files": files,
        "real_play": {
            "model": "real_play_v1", "verdict": "WON_ROBUST", "exitCode": 0,
            "levelSha256": result["levelSha256"], "planSha256": result["planSha256"],
            "gameCommit": result["gameCommit"], "resultFile": str(result_path),
            "resultSha256": files["real_play_result"]["sha256"],
        },
    }
    assert release_pool._validate_release_entry_real_play(entry, "fixture.json") is False


def test_release_pool_accepts_only_complete_canonical_60hz_proof(tmp_path: Path) -> None:
    fixture = _fixture(tmp_path)
    level, plan = Path(fixture["level"]), Path(fixture["plan"])
    result_path = Path(fixture["run"]) / "real_play_result_v2.json"
    result = _result(fixture)
    result_path.write_text(json.dumps(result), encoding="utf-8")
    files = {
        "level": {"path": str(level), "sha256": _sha(level.read_bytes())},
        "supply_plan": {"path": str(plan), "sha256": _sha(plan.read_bytes())},
        "real_play_result": {"path": str(result_path), "sha256": _sha(result_path.read_bytes())},
    }
    entry = {
        "files": files,
        "candidate_classification": {"source_sha256": result["sourceSha256"]},
        "real_play": {
            "model": result["model"], "verdict": result["verdict"], "exitCode": 0,
            "resultSchema": result["schema"], "mode": result["mode"],
            "sourceSha256": result["sourceSha256"], "runId": result["runId"],
            "timestamp": result["timestamp"], "levelSha256": result["levelSha256"],
            "planSha256": result["planSha256"], "gameCommit": result["gameCommit"],
            "resultFile": str(result_path), "resultSha256": files["real_play_result"]["sha256"],
        },
    }
    assert release_pool._validate_release_entry_real_play(entry, "canonical.json") is True
    result["perDt"]["1/60"]["final"]["targetsCleared"] = False
    changed_raw = json.dumps(result).encode("utf-8")
    result_path.write_bytes(changed_raw)
    changed_sha = _sha(changed_raw)
    files["real_play_result"]["sha256"] = changed_sha
    entry["real_play"]["resultSha256"] = changed_sha
    with pytest.raises(release_pool.ReleaseError, match="canonical 60-Hz result is incomplete"):
        release_pool._validate_release_entry_real_play(entry, "canonical.json")


def test_ready_writer_keeps_solver_replay_and_real_play_as_separate_required_proofs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    factory = tmp_path / "factory"
    run_dir = factory / "data" / "Release Pool" / "Pending" / "Pipelines" / "Work" / "candidate-owner-test" / "run"
    bundle_dir = factory / "bundles" / "owner-test"
    run_dir.mkdir(parents=True)
    bundle_dir.mkdir(parents=True)
    output_dir = factory / "level_factory" / "output" / "studio-extensions"
    pipeline_path = factory / "data" / "Release Pool" / "Ready" / "Pipelines" / "run-one.json"
    pipeline_path.parent.mkdir(parents=True)
    artwork = bundle_dir / "artwork.png"
    artwork.write_bytes(b"test artwork")
    level = run_dir / "level.json"
    plan = run_dir / "plan.json"
    real_play_path = run_dir / "real_play_result_v2.json"
    level.write_text('{"id":"level_fake"}\n', encoding="utf-8")
    plan.write_text('{"levelId":"level_fake","intendedColumnClicks":[1]}\n', encoding="utf-8")
    source_sha = "b" * 64
    real_play_body = {
        "schema": "scrubbots.real_play_file_result.v2", "model": "real_play_v1",
        "mode": "canonical_60hz", "canonicalDt": "1/60", "verdict": "WON_CANONICAL", "exitCode": 0,
        "levelFile": str(level.resolve()), "planFile": str(plan.resolve()), "levelId": "level_fake",
        "levelSha256": _normalized_sha(level), "planSha256": _normalized_sha(plan), "planClicks": [1],
        "sourceSha256": source_sha, "gameCommit": "c" * 40, "runId": "fixture-run", "timestamp": "2026-11-07T12:00:00Z",
        "searched": False,
        "perDt": {"1/60": {"won": True, "final": {"supplyExhausted": True, "targetsCleared": True,
            "slotsEmpty": True, "activeRobots": 0, "boardResidue": 0}}},
    }
    real_play_path.write_text(json.dumps(real_play_body), encoding="utf-8")
    candidate = {
        "candidate_id": "candidate-owner-test", "source_path": "bundles/owner-test",
        "artwork_sha256": _sha(artwork.read_bytes()), "grid_hash": "grid-hash", "width": 1,
        "height": 1, "used_colors": ["C01"],
    }
    pipeline: dict[str, Any] = {
        "run_id": "run-one", "version": 2, "disposition": "READY", "primary": {
            "state": "READY", "acceptance": {"solver_status": "SOLVED", "replay": "WIN"},
            "difficulty": {"class": "MEDIUM"},
            "files": {"level": str(level), "supply_plan": str(plan), "real_play_result": str(real_play_path)},
        },
    }
    pipeline_path.write_text(json.dumps(pipeline), encoding="utf-8")
    classification = {"source_sha256": source_sha}
    monkeypatch.setattr(release_pool, "validate_pool_candidate_provenance", lambda *_args: classification)
    monkeypatch.setattr(release_pool, "_candidate_source_lineage", lambda _candidate: {"source_id": "owner-test"})
    monkeypatch.setattr(studio_extensions, "verify_owner_source", lambda *_args: {"source_sha256": source_sha, "source_bytes_sha256": source_sha})
    monkeypatch.setattr(studio_extensions, "_repository_root", lambda: factory)
    monkeypatch.setattr(release_pool, "_canonical_official_difficulty", lambda _primary: {"challengeScore": 50.0, "vector": [0.1] * 7, "profile": {"dominant": "FLOW"}})
    monkeypatch.setattr(release_pool, "_official_challenge_vector", lambda _official: [0.1] * 7)
    monkeypatch.setattr(release_pool, "_resolve_official_profile", lambda *_args: ({"dominant": "FLOW"}, {"kind": "DERIVED"}))
    monkeypatch.setattr(release_pool, "_validate_score_and_class", lambda *_args: None)
    monkeypatch.setattr(studio_extensions, "_pipeline_path", lambda _run_id, **_kwargs: pipeline_path)

    pooled = release_pool.enter_release_pool(candidate, pipeline)
    entry_path = factory / "data" / "Release Pool" / "Ready" / "candidate-owner-test-run-one-ready.json"
    entry = json.loads(entry_path.read_text(encoding="utf-8"))
    assert pooled["disposition"] == "ENTERED_RELEASE_POOL"
    assert entry["real_play"]["verdict"] == "WON_CANONICAL"
    assert entry["real_play"]["storagePolicy"] == release_pool.CANONICAL_WORK_STORAGE_POLICY
    assert entry["files"]["real_play_result"]["path"].endswith("real_play_result_v2.json")
    assert entry["files"]["supply_plan"]["sha256"] == _sha(plan.read_bytes())
    assert release_pool._validate_release_entry_real_play(entry, entry_path.name) is True
    external_level = tmp_path / "external-level.json"
    external_level.write_bytes(level.read_bytes())
    moved_reference = json.loads(json.dumps(entry))
    moved_reference["files"]["level"]["path"] = str(external_level)
    with pytest.raises(release_pool.ReleaseError, match="canonical work evidence is unavailable"):
        release_pool._validate_release_entry_real_play(moved_reference, entry_path.name)

    from scrubbots_pixel_factory import owner_art_storage
    is_reparse_point = owner_art_storage._is_reparse_point
    with monkeypatch.context() as scoped:
        scoped.setattr(owner_art_storage, "_is_reparse_point", lambda path: Path(path) == real_play_path or is_reparse_point(Path(path)))
        with pytest.raises(release_pool.ReleaseError, match="result is a symlink or reparse point"):
            release_pool._pipeline_real_play_proof(
                pipeline["primary"], {"level": level, "supply_plan": plan}, source_sha,
            )

    mismatched_mapping = json.loads(json.dumps(pipeline))
    mismatched_mapping["primary"]["files"]["level"] = str(output_dir / "forged-level.json")
    with pytest.raises(release_pool.ReleaseError, match="differs from its canonical persisted record"):
        release_pool.enter_release_pool(candidate, mismatched_mapping)
    numeric_type_mismatch = json.loads(json.dumps(pipeline))
    numeric_type_mismatch["version"] = 2.0
    with pytest.raises(release_pool.ReleaseError, match="differs from its canonical persisted record"):
        release_pool.enter_release_pool(candidate, numeric_type_mismatch)

    external_plan = tmp_path / "external-plan.json"
    external_plan.write_bytes(plan.read_bytes())
    pipeline["primary"]["files"]["supply_plan"] = str(external_plan)
    pipeline_path.write_text(json.dumps(pipeline), encoding="utf-8")
    with pytest.raises(release_pool.ReleaseError, match="escapes Release Pool work"):
        release_pool.enter_release_pool(candidate, pipeline)

    pipeline["primary"]["acceptance"]["replay"] = "LOSE"
    result = release_pool.enter_release_pool(candidate, pipeline)
    assert result["disposition"] == "NOT_ENTERED_NOT_READY"
    assert "solver and replay WIN" in result["reason"]
