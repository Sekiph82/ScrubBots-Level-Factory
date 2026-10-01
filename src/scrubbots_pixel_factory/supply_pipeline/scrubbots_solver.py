"""ScrubBotsSolver: the ACCEPTANCE authority. Runs the game's own SolvabilitySolver,
SolvabilitySolver.replay and LevelDifficultyAnalyzerV1 through godot/solver_bridge.gd."""
import json
import subprocess
import tempfile
from pathlib import Path

from .game_rules import find_godot

BRIDGE = Path(__file__).resolve().parent / "godot" / "solver_bridge.gd"
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


class ScrubBotsSolver:
    def __init__(self, rules, godot=None):
        self.rules = rules
        self.godot = godot or find_godot()
        if not self.godot:
            raise RuntimeError("Godot not found (set SCRUBBOTS_GODOT or put godot on PATH)")

    def run(self, level, candidates, stop_after=1, max_visited=None, analyze=True,
            level_number=1, progress=None, timeout=None):
        """level: {id,width,height,palette:[#RRGGBBAA local],cells:[local or -1]}
        candidates: [{id, columns:[[{color,count}]*3]} or {..., replay_trace:[...]}]"""
        work = Path(tempfile.mkdtemp(prefix="sb_bridge_"))
        req = {"level": level, "candidates": candidates, "stop_after_solved": stop_after,
               "analyze": analyze, "level_number": level_number,
               "game_authority": dict(self.rules.authority)}
        if max_visited:
            req["max_visited"] = max_visited
        (work / "req.json").write_text(json.dumps(req), encoding="utf-8")
        tail = []
        with subprocess.Popen([self.godot, "--headless", "--path", str(self.rules.project), "-s", str(BRIDGE),
                               "--", str(work / "req.json"), str(work / "res.json")],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                              encoding="utf-8", errors="replace", creationflags=NO_WINDOW) as p:
            for line in p.stdout:
                line = line.rstrip()
                tail = (tail + [line])[-30:]
                if line.startswith("BRIDGE") and progress:
                    progress(line)
            p.wait(timeout=timeout)
        out = work / "res.json"
        if p.returncode != 0 or not out.exists():
            raise RuntimeError("solver bridge failed:\n" + "\n".join(tail))
        return json.loads(out.read_text(encoding="utf-8"))

