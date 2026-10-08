"""Fail-closed proof that the configured current ScrubBots game supports VOID V2."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any


REPOSITORY = "Sekiph82/Scrubbots"
AUDITED_VOID_COMMIT = "7d0d148b8609ec04852fdee02f6b8ef37598c616"
VOID_CELL = -1
FORMAT_VERSION_VOID = 2
_EXPECTED_ORIGINS = {
    f"https://github.com/{REPOSITORY}.git",
    f"https://github.com/{REPOSITORY}",
}


def _git(project: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(project), *args],
        text=True,
        stderr=subprocess.DEVNULL,
    ).strip()


def void_capability(project: str | Path | None = None) -> dict[str, Any]:
    """Return explicit OPEN/CLOSED evidence for the configured clean current game authority.

    This performs local reads only. It never fetches, guesses a sibling checkout, or
    falls back to a Desktop game project; the caller must configure ``project`` or
    ``SCRUBBOTS_PROJECT`` before transparent artwork can enter production.
    """

    if project is None:
        import os

        project = os.environ.get("SCRUBBOTS_PROJECT")
    if not project:
        return _closed("SCRUBBOTS_PROJECT is not configured for current-game authority.")
    root = Path(project).expanduser().resolve()
    if not (root / "project.godot").is_file():
        return _closed("Configured ScrubBots project is missing project.godot.")
    try:
        top = Path(_git(root, "rev-parse", "--show-toplevel")).resolve()
        origin = _git(root, "remote", "get-url", "origin").rstrip("/")
        branch = _git(root, "branch", "--show-current")
        head = _git(root, "rev-parse", "HEAD")
        current_main = _git(root, "rev-parse", "refs/remotes/origin/main")
        status = _git(root, "status", "--porcelain")
        ancestor = subprocess.run(
            ["git", "-C", str(root), "merge-base", "--is-ancestor", AUDITED_VOID_COMMIT, "HEAD"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode == 0
    except (OSError, subprocess.CalledProcessError):
        return _closed("Configured ScrubBots authority is not a readable Git checkout with origin/main.")
    if top != root or origin not in _EXPECTED_ORIGINS:
        return _closed("Configured project root or canonical ScrubBots origin does not match.")
    if branch not in {"main", ""} or head != current_main or status:
        return _closed("Configured ScrubBots authority must be clean and equal exact origin/main.", head=head)
    if not ancestor:
        return _closed("Current ScrubBots main does not contain the audited VOID implementation.", head=head)

    adr_path = root / "docs" / "05_TECH_DECISIONS.md"
    spec_path = root / "docs" / "03_LEVEL_DATA_SPEC.md"
    code_path = root / "scripts" / "data" / "level_data.gd"
    try:
        adr = adr_path.read_text(encoding="utf-8")
        spec = spec_path.read_text(encoding="utf-8")
        code = code_path.read_text(encoding="utf-8")
    except OSError:
        return _closed("Current ScrubBots VOID ADR, Level Data spec, or LevelData source is unavailable.", head=head)
    contract_ok = (
        re.search(r"const\s+FORMAT_VERSION_VOID\s*:?=\s*2\b", code) is not None
        and re.search(r"const\s+VOID_CELL\s*:?=\s*-1\b", code) is not None
        and "### ADR-030: VOID cells" in adr
        and "D1 presentation" in adr
        and re.search(r">=\s*200\s+non-VOID\s+cells\s+AND\s+>=\s*25%", adr, re.IGNORECASE) is not None
        and "Version 2: VOID cells" in spec
        and "version" in spec and "2" in spec and "VOID_CELL" in spec
        and "get_artwork_cell_count()" in spec
    )
    if not contract_ok:
        return _closed("Current ScrubBots VOID V2 constants or inherited ADR/spec contracts are absent or incompatible.", head=head)
    return {
        "state": "OPEN",
        "disposition": "READY",
        "repository": REPOSITORY,
        "branch": "main",
        "git_head": head,
        "audited_commit": AUDITED_VOID_COMMIT,
        "level_data_version_void": FORMAT_VERSION_VOID,
        "void_cell": VOID_CELL,
        "adr": "docs/05_TECH_DECISIONS.md#ADR-030",
        "level_data_spec": "docs/03_LEVEL_DATA_SPEC.md",
        "d1": "VOID renders exactly like CLEARED/BG01",
        "d2": {"minimum_artwork_cells": 200, "minimum_artwork_ratio": 0.25},
    }


def _closed(reason: str, *, head: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"state": "CLOSED", "disposition": "UNAVAILABLE", "reason": reason}
    if head:
        result["git_head"] = head
    return result


__all__ = ["AUDITED_VOID_COMMIT", "FORMAT_VERSION_VOID", "REPOSITORY", "VOID_CELL", "void_capability"]
