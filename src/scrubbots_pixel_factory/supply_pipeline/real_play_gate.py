"""Fail-closed adapter for the ScrubBots real-play file-mode verifier."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


RESULT_SCHEMA = "scrubbots.real_play_file_result.v1"
REAL_PLAY_MODEL = "real_play_v1"
SUPPORTED_VERDICTS = {
    "WON_ROBUST",
    "WON_CANONICAL_ONLY",
    "LOST",
    "SEARCH_EXHAUSTED",
    "SEARCH_BUDGET",
    "INVALID_INPUT",
}
DEFAULT_SCRUBBOTS_REPO = Path("C:/Users/sekip/Desktop/ScrubBots")
DEFAULT_GODOT_EXE = Path(
    "C:/Users/sekip/AppData/Local/Microsoft/WinGet/Packages/"
    "GodotEngine.GodotEngine_Microsoft.Winget.Source_8wekyb3d8bbwe/"
    "Godot_v4.7.2-stable_win64_console.exe"
)
DEFAULT_TIMEOUT_SECONDS = 900.0
_CLICK_ARRAY = re.compile(r'("intendedColumnClicks"\s*:\s*)\[[^\]]*\]')


class RealPlayGateError(ValueError):
    """A real-play preflight or result failed closed."""


def resolve_real_play_settings(
    settings: dict[str, Any] | None = None,
    environ: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Resolve Studio settings, then environment fallbacks, then owner defaults."""

    configured = settings if isinstance(settings, dict) else {}
    env = os.environ if environ is None else environ

    def value(key: str, env_key: str, fallback: Any) -> Any:
        setting = configured.get(key)
        if setting is not None and str(setting).strip():
            return setting
        from_env = env.get(env_key, "")
        return from_env if str(from_env).strip() else fallback

    repo = value(
        "scrubbotsRepoPath",
        "SCRUBBOTS_REPO",
        env.get("SCRUBBOTS_PROJECT", str(DEFAULT_SCRUBBOTS_REPO)),
    )
    godot = value("godotExe", "GODOT", DEFAULT_GODOT_EXE)
    timeout = value("realPlayTimeoutSeconds", "SCRUBBOTS_REAL_PLAY_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)
    return {
        "scrubbotsRepoPath": str(repo).strip(),
        "godotExe": str(godot).strip(),
        "realPlayTimeoutSeconds": timeout,
    }


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def _read_json_object(path: Path, label: str) -> tuple[bytes, str, dict[str, Any]]:
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        value = json.loads(text, object_pairs_hook=_strict_object)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise RealPlayGateError(f"{label} is unreadable or invalid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise RealPlayGateError(f"{label} JSON root must be an object: {path}")
    normalized = raw.replace(b"\r\n", b"\n")
    return raw, hashlib.sha256(normalized).hexdigest(), value


def _resolve_executable(value: str) -> Path:
    configured = Path(value).expanduser()
    if configured.is_file():
        return configured.resolve()
    discovered = shutil.which(value)
    if discovered:
        return Path(discovered).resolve()
    raise RealPlayGateError(
        f"godotExe setting is invalid: executable not found at {value!r}; "
        "set GODOT or choose the Godot 4.7.2 console executable in Studio Settings."
    )


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except (OSError, ValueError):
        return False


def _preflight(
    settings: dict[str, Any] | None,
    environ: dict[str, str] | None,
) -> tuple[dict[str, Any], Path, Path, float, dict[str, str] | None]:
    resolved = resolve_real_play_settings(settings, environ)
    repo_setting = resolved["scrubbotsRepoPath"]
    repo = Path(repo_setting).expanduser()
    if not repo.is_absolute():
        raise RealPlayGateError(
            f"scrubbotsRepoPath setting must be an absolute path; found {repo_setting!r}. "
            "Set SCRUBBOTS_REPO or choose the ScrubBots checkout in Studio Settings."
        )
    repo = repo.resolve()
    missing = [str(path) for path in (repo / "project.godot", repo / "tools" / "real_play_file.gd") if not path.is_file()]
    if missing:
        raise RealPlayGateError(
            f"scrubbotsRepoPath setting is invalid: {repo}; missing " + ", ".join(missing)
        )
    executable = _resolve_executable(resolved["godotExe"])
    try:
        timeout = float(resolved["realPlayTimeoutSeconds"])
    except (TypeError, ValueError) as exc:
        raise RealPlayGateError("realPlayTimeoutSeconds setting must be a positive number") from exc
    if not math.isfinite(timeout) or timeout <= 0:
        raise RealPlayGateError("realPlayTimeoutSeconds setting must be a positive finite number")
    process_env = None if environ is None else dict(environ)
    try:
        version = subprocess.run(
            [str(executable), "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=min(timeout, 15.0),
            shell=False,
            env=process_env,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RealPlayGateError("godotExe preflight timed out while checking --version") from exc
    except OSError as exc:
        raise RealPlayGateError(f"godotExe setting could not be started: {exc}") from exc
    reported = version.stdout.strip()
    if version.returncode != 0 or not reported.startswith("4.7.2"):
        raise RealPlayGateError(
            f"godotExe preflight failed: expected version 4.7.2; found {reported!r} "
            f"(exit {version.returncode}). Check the godotExe Studio setting."
        )
    return resolved, repo, executable, timeout, process_env


def _parse_result_line(stdout: str) -> dict[str, Any]:
    markers = [line[len("REAL_PLAY_RESULT ") :] for line in stdout.splitlines() if line.startswith("REAL_PLAY_RESULT ")]
    if not markers:
        raise RealPlayGateError("real_play_v1 returned no REAL_PLAY_RESULT line; candidate is not ready")
    try:
        result = json.loads(markers[-1], object_pairs_hook=_strict_object)
    except (json.JSONDecodeError, ValueError) as exc:
        raise RealPlayGateError(f"last REAL_PLAY_RESULT line contains invalid JSON: {exc}") from exc
    if not isinstance(result, dict):
        raise RealPlayGateError("last REAL_PLAY_RESULT JSON value is not an object")
    return result


def _validate_result(
    result: dict[str, Any],
    process_exit: int,
    level_path: Path,
    plan_path: Path,
    level_id: str,
    plan_clicks: list[int],
    level_sha: str,
    plan_sha: str,
    allow_search: bool,
) -> None:
    if result.get("schema") != RESULT_SCHEMA:
        raise RealPlayGateError(f"real_play_v1 result has wrong schema: {result.get('schema')!r}")
    if result.get("model") != REAL_PLAY_MODEL:
        raise RealPlayGateError(f"real_play_v1 result has wrong model: {result.get('model')!r}")
    if type(result.get("exitCode")) is not int or result["exitCode"] != process_exit:
        raise RealPlayGateError(
            f"real_play_v1 exitCode mismatch: process={process_exit}, result={result.get('exitCode')!r}"
        )
    if result.get("verdict") not in SUPPORTED_VERDICTS:
        raise RealPlayGateError(f"real_play_v1 returned unsupported verdict: {result.get('verdict')!r}")
    expected_exit = 0 if result["verdict"] == "WON_ROBUST" else 2 if result["verdict"] == "INVALID_INPUT" else 1
    if process_exit != expected_exit:
        raise RealPlayGateError(
            f"real_play_v1 verdict/exit mismatch: {result['verdict']} with process exit {process_exit}"
        )
    if result["verdict"] == "INVALID_INPUT":
        if not isinstance(result.get("error"), str) or not result["error"]:
            raise RealPlayGateError("real_play_v1 INVALID_INPUT result omitted its error detail")
        return
    if result.get("levelFile") != str(level_path) or result.get("planFile") != str(plan_path):
        raise RealPlayGateError("real_play_v1 result paths do not match the exact files passed to the game")
    if result.get("levelId") != level_id:
        raise RealPlayGateError("real_play_v1 result levelId does not match the level and supply plan")
    if result.get("levelSha256") != level_sha:
        raise RealPlayGateError("real_play_v1 levelSha256 does not match the exact level bytes")
    if result.get("planSha256") != plan_sha:
        raise RealPlayGateError("real_play_v1 planSha256 does not match the exact supply-plan bytes")
    if result.get("planClicks") != plan_clicks or not isinstance(result.get("planClicks"), list):
        raise RealPlayGateError("real_play_v1 planClicks do not match intendedColumnClicks in the plan")
    if type(result.get("searched")) is not bool:
        raise RealPlayGateError("real_play_v1 result searched field is missing or malformed")
    if result["searched"] and not allow_search:
        raise RealPlayGateError("real_play_v1 reported searched=true for a run without --search")
    if not isinstance(result.get("gameCommit"), str) or not result["gameCommit"]:
        raise RealPlayGateError("real_play_v1 result gameCommit is missing")
    if result["verdict"] == "WON_ROBUST":
        per_dt = result.get("perDt")
        if not isinstance(per_dt, dict) or any(
            not isinstance(per_dt.get(dt), dict) or per_dt[dt].get("won") is not True
            for dt in ("1/30", "1/60", "1/120")
        ):
            raise RealPlayGateError("WON_ROBUST result does not prove wins at 1/30, 1/60, and 1/120")


def _invoke(
    executable: Path,
    repo: Path,
    level_path: Path,
    plan_path: Path,
    result_path: Path,
    timeout: float,
    plan: dict[str, Any],
    level: dict[str, Any],
    level_sha: str,
    plan_sha: str,
    *,
    search: bool,
    process_env: dict[str, str] | None,
) -> dict[str, Any]:
    arguments = [
        str(executable),
        "--headless",
        "--path",
        str(repo),
        "-s",
        "res://tools/real_play_file.gd",
        "--",
        "--level-file",
        str(level_path),
        "--plan-file",
        str(plan_path),
        "--out",
        str(result_path),
    ]
    if search:
        arguments.append("--search")
    try:
        completed = subprocess.run(
            arguments,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False,
            env=process_env,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RealPlayGateError(
            f"real_play_v1 timed out after {timeout:g}s; candidate is not ready"
        ) from exc
    except OSError as exc:
        raise RealPlayGateError(f"real_play_v1 process could not be started: {exc}") from exc

    result = _parse_result_line(completed.stdout)
    if not result_path.is_file():
        raise RealPlayGateError("real_play_v1 did not write the requested result evidence file")
    try:
        written_result = json.loads(result_path.read_text(encoding="utf-8"), object_pairs_hook=_strict_object)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise RealPlayGateError(f"real_play_v1 --out evidence is unreadable or invalid JSON: {exc}") from exc
    if written_result != result:
        raise RealPlayGateError("REAL_PLAY_RESULT stdout object differs from the --out evidence object")

    clicks = plan.get("intendedColumnClicks")
    if not isinstance(clicks, list) or any(type(click) is not int for click in clicks):
        raise RealPlayGateError("supply plan intendedColumnClicks must be an array of integers")
    _validate_result(
        result,
        completed.returncode,
        level_path,
        plan_path,
        str(plan.get("levelId", "")),
        clicks,
        level_sha,
        plan_sha,
        search,
    )
    if result.get("verdict") != "INVALID_INPUT" and result.get("levelId") != level.get("id"):
        raise RealPlayGateError("supply plan levelId does not match the exact level id")
    return result


def _format_rejection(result: dict[str, Any], result_path: Path) -> str:
    verdict = str(result.get("verdict", "UNKNOWN"))
    if verdict == "INVALID_INPUT":
        detail = f"export bug: {result.get('error') or 'no error detail'}"
    elif verdict == "LOST":
        per_dt = result.get("perDt", {})
        canonical = per_dt.get("1/60", {}) if isinstance(per_dt, dict) else {}
        stuck = canonical.get("stuckClickIndex") if isinstance(canonical, dict) else None
        slots = canonical.get("slots") if isinstance(canonical, dict) else None
        slot_states = []
        if isinstance(slots, list):
            slot_states = [
                f"slot {slot.get('index')}: {slot.get('state')}"
                for slot in slots
                if isinstance(slot, dict)
            ]
        detail = f"stuck after click {stuck}; " + (", ".join(slot_states) if slot_states else "slot state unavailable")
    elif verdict == "WON_CANONICAL_ONLY":
        detail = "wins at 1/60 only; failed a sensitivity dt"
    elif verdict == "SEARCH_EXHAUSTED":
        detail = "no supply-column order won under real play"
    elif verdict == "SEARCH_BUDGET":
        detail = "search budget exhausted without a robust win"
    else:
        detail = "real-play verdict did not authorize readiness"
    return f"real_play_v1 {verdict}: {detail}. Result evidence: {result_path}"


def _replace_plan_clicks(plan_path: Path, original: bytes, plan: dict[str, Any], clicks: list[int]) -> tuple[dict[str, Any], str]:
    if not clicks or any(type(click) is not int or click < 1 for click in clicks):
        raise RealPlayGateError("searchedClicks must be a non-empty array of positive integer columns")
    text = original.decode("utf-8")
    matches = list(_CLICK_ARRAY.finditer(text))
    if len(matches) != 1:
        raise RealPlayGateError("supply plan must contain exactly one intendedColumnClicks array")
    match = matches[0]
    replacement = match.group(1) + json.dumps(clicks, separators=(",", ":"))
    rewritten = text[: match.start()] + replacement + text[match.end() :]
    try:
        updated = json.loads(rewritten, object_pairs_hook=_strict_object)
    except (json.JSONDecodeError, ValueError) as exc:
        raise RealPlayGateError(f"searched click order could not be spliced into the supply plan: {exc}") from exc
    if not isinstance(updated, dict):
        raise RealPlayGateError("rewritten supply plan is not a JSON object")
    before = {key: value for key, value in plan.items() if key != "intendedColumnClicks"}
    after = {key: value for key, value in updated.items() if key != "intendedColumnClicks"}
    if before != after or updated.get("intendedColumnClicks") != clicks:
        raise RealPlayGateError("rewriting intendedColumnClicks changed another supply-plan value")
    if plan_path.read_bytes() != original:
        raise RealPlayGateError("supply plan changed during real-play search; refusing to overwrite it")
    temp_path = plan_path.with_name(f".{plan_path.name}.real-play-{os.getpid()}.tmp")
    created = False
    try:
        with temp_path.open("xb") as stream:
            created = True
            stream.write(rewritten.encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp_path, plan_path.stat().st_mode)
        os.replace(temp_path, plan_path)
        created = False
    except OSError as exc:
        raise RealPlayGateError(f"could not safely replace intendedColumnClicks in the supply plan: {exc}") from exc
    finally:
        if created:
            try:
                temp_path.unlink()
            except OSError:
                pass
    normalized = rewritten.encode("utf-8").replace(b"\r\n", b"\n")
    return updated, hashlib.sha256(normalized).hexdigest()


def ensure_real_play_gate(
    level_file: str | Path,
    plan_file: str | Path,
    result_file: str | Path,
    *,
    settings: dict[str, Any] | None = None,
    studio_root: str | Path | None = None,
    environ: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Run real_play_v1 and require a hash-bound robust win before acceptance."""

    from .. import studio_extensions as studio

    resolved, game_repo, executable, timeout, process_env = _preflight(settings, environ)
    root = Path(studio_root).resolve() if studio_root is not None else studio._repository_root().resolve()
    level_path = Path(level_file).expanduser()
    plan_path = Path(plan_file).expanduser()
    result_path = Path(result_file).expanduser()
    for label, path in (("level", level_path), ("supply plan", plan_path), ("result", result_path)):
        if not path.is_absolute():
            raise RealPlayGateError(f"{label} path must be absolute: {path}")
    if result_path.is_symlink():
        raise RealPlayGateError(f"real-play result path must not be a symbolic link: {result_path}")
    level_path = level_path.resolve()
    plan_path = plan_path.resolve()
    result_path = result_path.resolve()
    for label, path in (("level", level_path), ("supply plan", plan_path)):
        if not path.is_file():
            raise RealPlayGateError(f"{label} file is missing: {path}")
        if not _inside(path, root):
            raise RealPlayGateError(f"{label} file is outside the canonical Factory Studio project: {path}")
        if _inside(path, game_repo):
            raise RealPlayGateError(f"{label} file is inside the ScrubBots game repository: {path}")
    if result_path.parent != level_path.parent or result_path.parent != plan_path.parent:
        raise RealPlayGateError("real-play result must be stored beside the exact level and supply-plan evidence")
    if not result_path.parent.is_dir():
        raise RealPlayGateError(f"real-play evidence folder does not exist: {result_path.parent}")
    if _inside(result_path, game_repo):
        raise RealPlayGateError(f"real-play result path is inside the ScrubBots game repository: {result_path}")
    _level_raw, level_sha, level = _read_json_object(level_path, "level")
    plan_raw, plan_sha, plan = _read_json_object(plan_path, "supply plan")
    clicks = plan.get("intendedColumnClicks")
    if not isinstance(clicks, list) or not clicks or any(type(click) is not int or click < 1 for click in clicks):
        raise RealPlayGateError("supply plan intendedColumnClicks must be a non-empty array of positive integer columns")
    if not isinstance(plan.get("levelId"), str) or plan.get("levelId") != level.get("id"):
        raise RealPlayGateError("supply plan levelId must exactly match the level id")
    if not result_path.is_file() and result_path.exists():
        raise RealPlayGateError(f"real-play evidence path is not a regular file: {result_path}")

    initial = _invoke(
        executable,
        game_repo,
        level_path,
        plan_path,
        result_path,
        timeout,
        plan,
        level,
        level_sha,
        plan_sha,
        search=False,
        process_env=process_env,
    )
    if initial.get("verdict") == "WON_ROBUST" and initial.get("searched") is False:
        result = initial
    elif initial.get("verdict") in {"LOST", "WON_CANONICAL_ONLY"}:
        searched = _invoke(
            executable,
            game_repo,
            level_path,
            plan_path,
            result_path,
            timeout,
            plan,
            level,
            level_sha,
            plan_sha,
            search=True,
            process_env=process_env,
        )
        if searched.get("verdict") != "WON_ROBUST" or searched.get("searched") is not True:
            raise RealPlayGateError(_format_rejection(searched, result_path))
        search_result = searched.get("search")
        if not isinstance(search_result, dict) or search_result.get("status") != "SOLVED" or search_result.get("robust") is not True:
            raise RealPlayGateError("real_play_v1 search result did not prove a robust SOLVED order")
        searched_clicks = searched.get("searchedClicks")
        if not isinstance(searched_clicks, list) or len(searched_clicks) != len(clicks):
            raise RealPlayGateError("real_play_v1 search returned a missing or wrong-length searchedClicks order")
        plan, plan_sha = _replace_plan_clicks(plan_path, plan_raw, plan, searched_clicks)
        result = _invoke(
            executable,
            game_repo,
            level_path,
            plan_path,
            result_path,
            timeout,
            plan,
            level,
            level_sha,
            plan_sha,
            search=False,
            process_env=process_env,
        )
        if result.get("verdict") != "WON_ROBUST" or result.get("searched") is not False:
            raise RealPlayGateError(_format_rejection(result, result_path))
    else:
        raise RealPlayGateError(_format_rejection(initial, result_path))

    return {
        "result": result,
        "result_path": str(result_path),
        "result_sha256": hashlib.sha256(result_path.read_bytes()).hexdigest(),
        "level_sha256": level_sha,
        "plan_sha256": plan_sha,
        "settings": resolved,
    }


__all__ = ["RealPlayGateError", "ensure_real_play_gate", "resolve_real_play_settings"]
