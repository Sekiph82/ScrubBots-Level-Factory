"""Current ScrubBots authority discovered from the canonical game checkout.

The supply contract deliberately has no global robot-count cap.  A plan carries
its own positive ``maxRobotsPerBatch`` metadata bound and the game validates that
bound for each plan.
"""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from .contracts import BASELINE_SLOT_COUNT, VISIBLE_PREVIEW_DEPTH, validate_column_count

def _gd_const(path, name):
    m = re.search(rf"const\s+{name}(?:\s*:\s*[A-Za-z_][A-Za-z0-9_]*)?\s*(?::=|=)\s*(\d+)", Path(path).read_text(encoding="utf-8"))
    if not m:
        raise RuntimeError(f"constant {name} not found in {path}")
    return int(m.group(1))


def _gd_const_optional(path, name):
    m = re.search(rf"const\s+{name}(?:\s*:\s*[A-Za-z_][A-Za-z0-9_]*)?\s*(?::=|=)\s*(\d+)", Path(path).read_text(encoding="utf-8"))
    return int(m.group(1)) if m else None


def find_godot():
    """Godot executable: SCRUBBOTS_GODOT env, PATH (godot4/godot) or the winget link."""
    env = os.environ.get("SCRUBBOTS_GODOT")
    if env and Path(env).exists():
        return env
    for name in ("godot4", "godot"):
        p = shutil.which(name)
        if p:
            return p
    link = Path.home() / "AppData/Local/Microsoft/WinGet/Links/godot.exe"
    return str(link) if link.exists() else None


class GameRules:
    def __init__(self, project=None, batch_cap="none", column_count=None):
        """Read the current game's dimensions, palette and difficulty authority.

        ``batch_cap`` is retained as a compatibility argument for callers that
        used the owner ZIP API, but is intentionally ignored: global caps are not
        part of the current game contract.
        """
        configured_project = project or os.environ.get("SCRUBBOTS_PROJECT")
        self._void_project_configured = configured_project is not None
        if not configured_project:
            raise FileNotFoundError("SCRUBBOTS_PROJECT or an explicit game_project is required; implicit Desktop fallback is disabled")
        p = Path(configured_project)
        if not (p / "project.godot").exists():
            raise FileNotFoundError(f"ScrubBots project not found: {p}")
        self.project = p
        self.authority = self._authority_identity(p)
        loader = p / "scripts/gameplay/supply/supply_plan_loader.gd"
        self.loader_cap = None
        self.max_robots_per_batch = None
        fixed_columns = _gd_const_optional(loader, "COLUMN_COUNT")
        self.game_min_columns = _gd_const_optional(loader, "MIN_COLUMNS")
        self.game_max_columns = _gd_const_optional(loader, "MAX_COLUMNS")
        self.game_column_count = fixed_columns if fixed_columns is not None else self.game_min_columns
        if self.game_column_count is None:
            raise RuntimeError(f"column-count authority not found in {loader}")
        self.game_preview_depth = _gd_const(loader, "VISIBLE_PREVIEW_DEPTH")
        self.column_count = validate_column_count(
            self.game_column_count if column_count is None else column_count
        )
        self.preview_depth = VISIBLE_PREVIEW_DEPTH
        self.slot_count = _gd_const(p / "scripts/gameplay/solver/proof_state.gd", "SLOT_COUNT")
        self.baseline_slot_count = BASELINE_SLOT_COUNT
        prog = json.loads((p / "data/config/level_progression_v1.json").read_text(encoding="utf-8"))
        self.lanes = {k: float(v["base"]) for k, v in prog["lanes"].items()}
        pal = json.loads((p / "data/palettes/scrubbots_palette_v3.json").read_text(encoding="utf-8"))
        self.palette = [(c["id"], c["hex"].upper()) for c in pal["colors"]]  # [(C01, #FF4500), ...]

    @property
    def live_column_verification_available(self):
        """Whether the checked-out game loader can validate this product plan."""

        supports_selected = (
            self.game_min_columns is not None
            and self.game_max_columns is not None
            and self.game_min_columns <= self.column_count <= self.game_max_columns
        )
        fixed_matches = self.game_column_count == self.column_count
        return (supports_selected or fixed_matches) and self.game_preview_depth == self.preview_depth

    @staticmethod
    def _authority_identity(project: Path) -> dict[str, str]:
        try:
            head = subprocess.check_output(
                ["git", "-C", str(project), "rev-parse", "HEAD"],
                text=True, stderr=subprocess.DEVNULL,
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            head = "UNAVAILABLE"
        return {
            "repository": "Sekiph82/Scrubbots",
            "branch": "main",
            "git_head": head,
            "loader": "scripts/gameplay/supply/supply_plan_loader.gd",
            "solver": "scripts/gameplay/solver/solvability_solver.gd",
            "difficulty_v1": "scripts/difficulty/level_difficulty_analyzer_v1.gd",
        }

    def classify(self, challenge_score):
        """Difficulty class = nearest owner-locked lane base (level_progression_v1.json)."""
        return min(self.lanes, key=lambda k: abs(self.lanes[k] - challenge_score))

    def void_capability(self):
        """Current-game VOID gate; opaque V1 callers do not need this capability."""
        from .void_capability import void_capability

        return void_capability(self.project if self._void_project_configured else None)
