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
        # Exercise the game's owner-facing loaders for every candidate, including
        # generated candidates. SupplyPlanLoader resolves canonical global C IDs
        # through the live game's palette authority before building runtime state.
        cid_by_hex = {color.upper()[:7]: cid for cid, color in self.rules.palette}
        for index, candidate in enumerate(candidates):
            if "columns" not in candidate:
                continue
            columns = []
            maximum = 1
            for column_index, column in enumerate(candidate["columns"]):
                batches = []
                for batch_index, batch in enumerate(column):
                    amount = int(batch["count"])
                    maximum = max(maximum, amount)
                    local_color = int(batch["color"])
                    if local_color < 0 or local_color >= len(level["palette"]):
                        raise ValueError("candidate batch uses a palette index outside the level")
                    local_hex = str(level["palette"][local_color]).upper()[:7]
                    cid = cid_by_hex.get(local_hex)
                    if cid is None:
                        raise ValueError(f"level palette color {local_hex} is not in the current game's canonical palette")
                    batches.append({"batchId": f"C{index:04d}-K{column_index:02d}-B{batch_index:03d}",
                                    "cid": cid, "robots": amount})
                columns.append(batches)
            plan = {"schema": "scrubbots.level_supply_plan.v1", "version": 1,
                    "levelId": str(level["id"]), "columnCount": len(columns),
                    "visiblePreviewDepth": self.rules.preview_depth,
                    "maxRobotsPerBatch": maximum, "columns": columns}
            plan_path = work / f"plan-{index}.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            candidate["supply_plan_path"] = str(plan_path)
        req = {"level": level, "candidates": candidates, "column_count": self.rules.column_count,
               "visible_preview_depth": self.rules.preview_depth, "stop_after_solved": stop_after,
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
