"""Host adapter for the pure CPX-002 gate: exact TEMP Git authority + real Godot."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Mapping, Sequence

from scrubbots_content_pipeline.current_main_replay import (
    AUTHORITY_SOURCE_PATHS,
    GAME_REMOTE,
    CurrentMainReplayError,
    CurrentMainReplayReceipt,
    verify_current_main_supply_replay,
)

_MARKER = "CPX002_RESULT_JSON="
_GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
_ROOT = Path(__file__).resolve().parents[1]
_HARNESS = _ROOT / "tests" / "fixtures" / "cpx002_current_main_replay.gd"


def resolve_explicit_temp_game_authority(
    game_root: str | Path | None = None,
) -> Path:
    """Require the configured CPX-002 game authority to be an explicit TEMP checkout.

    This preflight is used before the authentic integration constructs a Factory
    solver-proven pack, because those Factory calls also consume
    ``SCRUBBOTS_PROJECT``. It intentionally rejects the game-rules module's
    legacy Desktop default instead of allowing the later replay gate to catch a
    mismatched authority after Factory work has already happened.
    """
    root = _explicit_temp_game_root(game_root)
    _authority_snapshot(root)
    return root


def _explicit_temp_game_root(game_root: str | Path | None) -> Path:
    configured = os.environ.get("SCRUBBOTS_PROJECT", "").strip()
    if not configured:
        raise CurrentMainReplayError("EXPLICIT_TEMP_GAME_AUTHORITY_REQUIRED")
    root = Path(configured).resolve()
    if game_root is not None and Path(game_root).resolve() != root:
        raise CurrentMainReplayError("GAME_AUTHORITY_ARGUMENT_MISMATCH")
    if not root.is_relative_to(Path(tempfile.gettempdir()).resolve()):
        raise CurrentMainReplayError("INVALID_GAME_AUTHORITY_ROOT")
    return root


def verify_staged_supply_with_current_main(
    *,
    staging_report,
    downloaded_manifest_bytes: bytes,
    downloaded_pack_bytes: Mapping[str, bytes],
    solver_identity_artifacts: Mapping[str, bytes],
    pack_build_evidence: Mapping[str, object],
    game_root: str | Path,
    godot_executable: str,
    timeout_seconds: int = 900,
) -> CurrentMainReplayReceipt:
    root = _explicit_temp_game_root(game_root)
    try:
        authority = _authority_snapshot(root)
    except CurrentMainReplayError as exc:
        return _blocked(str(exc), downloaded_manifest_bytes)
    except OSError:
        return _blocked("INVALID_GAME_AUTHORITY_SOURCE", downloaded_manifest_bytes)

    def recheck() -> Mapping[str, object]:
        return _authority_snapshot(root)

    def run_game(levels: Sequence[Mapping[str, object]]) -> Mapping[str, object]:
        with tempfile.TemporaryDirectory(prefix="cpx002-current-main-") as work:
            job_levels = []
            for item in levels:
                level_id = str(item["level_id"])
                level_path = Path(work) / f"{level_id}.level.json"
                plan_path = Path(work) / f"{level_id}.supply.json"
                level_path.write_bytes(item["level_data_bytes"])
                plan_path.write_bytes(item["supply_plan_bytes"])
                job_levels.append({
                    "level_id": level_id,
                    "level_path": str(level_path),
                    "plan_path": str(plan_path),
                    "level_sha256": item["level_sha256"],
                    "plan_sha256": item["plan_sha256"],
                    "fifo_columns": item["fifo_columns"],
                    "solver_state_sha256": item["solver_state_sha256"],
                    "solver_evidence_sha256": item["solver_evidence_sha256"],
                })
            job_path = Path(work) / "job.json"
            job_path.write_text(json.dumps({"levels": job_levels}, sort_keys=True), encoding="utf-8")
            return _run_godot(root, godot_executable, job_path, timeout_seconds)

    return verify_current_main_supply_replay(
        staging_report=staging_report,
        downloaded_manifest_bytes=downloaded_manifest_bytes,
        downloaded_pack_bytes=downloaded_pack_bytes,
        solver_identity_artifacts=solver_identity_artifacts,
        pack_build_evidence=pack_build_evidence,
        game_authority=authority,
        authority_check=recheck,
        game_runner=run_game,
    )


def _blocked(reason: str, manifest_bytes: bytes) -> CurrentMainReplayReceipt:
    return CurrentMainReplayReceipt(
        False, reason, "Sekiph82/Scrubbots", "main", "", {},
        hashlib.sha256(manifest_bytes).hexdigest() if type(manifest_bytes) is bytes else "",
        (),
    )


def _authority_snapshot(root: Path) -> dict[str, object]:
    temp_root = Path(tempfile.gettempdir()).resolve()
    if not root.is_relative_to(temp_root) or not root.is_dir():
        raise CurrentMainReplayError("INVALID_GAME_AUTHORITY_ROOT")
    remote = _git(root, "remote", "get-url", "origin").strip().rstrip("/")
    if remote.lower() != GAME_REMOTE.lower():
        raise CurrentMainReplayError("INVALID_GAME_AUTHORITY_REMOTE")
    _git(root, "fetch", "--prune", "origin")
    status = _git(root, "status", "--porcelain", "--untracked-files=all")
    try:
        branch = _git(root, "symbolic-ref", "--quiet", "--short", "HEAD").strip()
    except CurrentMainReplayError:
        branch = ""
    head = _git(root, "rev-parse", "HEAD").strip()
    main = _git(root, "rev-parse", "refs/remotes/origin/main").strip()
    if status or branch or head != main or not _GIT_SHA.fullmatch(head):
        raise CurrentMainReplayError("INVALID_GAME_AUTHORITY_CHECKOUT")
    source_hashes = {
        relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
        for relative in AUTHORITY_SOURCE_PATHS
    }
    return {
        "repository": "Sekiph82/Scrubbots",
        "branch": "main",
        "commit": head,
        "source_sha256": source_hashes,
    }


def _git(root: Path, *args: str) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, text=True, timeout=120
        )
    except subprocess.TimeoutExpired as exc:
        raise CurrentMainReplayError("GAME_AUTHORITY_GIT_TIMEOUT") from exc
    if proc.returncode:
        raise CurrentMainReplayError("GAME_AUTHORITY_GIT_FAILED")
    return proc.stdout


def _run_godot(root: Path, executable: str, job: Path, timeout_seconds: int) -> Mapping[str, object]:
    if not isinstance(timeout_seconds, int) or timeout_seconds < 1:
        raise CurrentMainReplayError("INVALID_TIMEOUT")
    try:
        proc = subprocess.run(
            [executable, "--headless", "--path", str(root), "--script", str(_HARNESS), "--", str(job)],
            capture_output=True, text=True, timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        raise CurrentMainReplayError("GAME_REPLAY_TIMEOUT") from exc
    for line in (proc.stdout + "\n" + proc.stderr).splitlines():
        if line.startswith(_MARKER):
            try:
                payload = json.loads(line[len(_MARKER):])
            except json.JSONDecodeError as exc:
                raise CurrentMainReplayError("GAME_REPLAY_INVALID_OUTPUT") from exc
            if not isinstance(payload, dict) or proc.returncode != 0:
                raise CurrentMainReplayError("GAME_REPLAY_ERROR")
            return payload
    raise CurrentMainReplayError("GAME_REPLAY_ERROR")


__all__ = ["resolve_explicit_temp_game_authority", "verify_staged_supply_with_current_main"]
