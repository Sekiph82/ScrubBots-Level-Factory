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

DEFAULT_PROJECT = Path.home() / "Desktop" / "Scrubbots"


def _gd_const(path, name):
    m = re.search(rf"const\s+{name}\s*:?=\s*(\d+)", Path(path).read_text(encoding="utf-8"))
    if not m:
        raise RuntimeError(f"constant {name} not found in {path}")
    return int(m.group(1))


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
    def __init__(self, project=None, batch_cap="none"):
        """Read the current game's dimensions, palette and difficulty authority.

        ``batch_cap`` is retained as a compatibility argument for callers that
        used the owner ZIP API, but is intentionally ignored: global caps are not
        part of the current game contract.
        """
        p = Path(project or os.environ.get("SCRUBBOTS_PROJECT") or DEFAULT_PROJECT)
        if not (p / "project.godot").exists():
            raise FileNotFoundError(f"ScrubBots project not found: {p}")
        self.project = p
        self.authority = self._authority_identity(p)
        loader = p / "scripts/gameplay/supply/supply_plan_loader.gd"
        self.loader_cap = None
        self.max_robots_per_batch = None
        self.column_count = _gd_const(loader, "COLUMN_COUNT")
        self.preview_depth = _gd_const(loader, "VISIBLE_PREVIEW_DEPTH")
        self.slot_count = _gd_const(p / "scripts/gameplay/solver/proof_state.gd", "SLOT_COUNT")
        prog = json.loads((p / "data/config/level_progression_v1.json").read_text(encoding="utf-8"))
        self.lanes = {k: float(v["base"]) for k, v in prog["lanes"].items()}
        pal = json.loads((p / "data/palettes/scrubbots_palette_v3.json").read_text(encoding="utf-8"))
        self.palette = [(c["id"], c["hex"].upper()) for c in pal["colors"]]  # [(C01, #FF4500), ...]

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
