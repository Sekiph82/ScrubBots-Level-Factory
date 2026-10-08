"""SupplyExporter: result JSON + game LevelData JSON and supply plan
(scrubbots.level_supply_plan.v1, loadable by the game's SupplyPlanLoader)."""
import hashlib
import json
from pathlib import Path


class SupplyExporter:
    def __init__(self, rules):
        self.rules = rules

    def export(self, result, out_dir, level_id):
        lv = result.get("_level", {})
        cells = lv.get("cells")
        palette = lv.get("palette")
        width, height = lv.get("width"), lv.get("height")
        if (not isinstance(cells, list) or any(type(value) is not int for value in cells)
                or not isinstance(palette, list) or not palette
                or type(width) is not int or type(height) is not int
                or width < 1 or height < 1 or len(cells) != width * height):
            raise ValueError("LevelData export requires integer cells, a palette, and matching positive dimensions")
        if any(value < -1 or value >= len(palette) for value in cells):
            raise ValueError("LevelData cells must be palette indices or canonical VOID -1")
        void_count = cells.count(-1)
        if void_count == len(cells):
            raise ValueError("LevelData cannot be all VOID; artwork is required")
        if void_count:
            gate_reader = getattr(self.rules, "void_capability", None)
            gate = gate_reader() if callable(gate_reader) else {"state": "CLOSED", "reason": "configured current-game VOID capability is unavailable"}
            if not isinstance(gate, dict) or gate.get("state") != "OPEN":
                reason = gate.get("reason", "current-game VOID capability gate is closed") if isinstance(gate, dict) else "current-game VOID capability gate is invalid"
                raise ValueError(f"TRANSPARENT_UNAVAILABLE: {reason}")
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        files = {}
        p = out / f"{level_id}_supply_result.json"
        public = lambda: {k: v for k, v in result.items() if not k.startswith("_")}
        p.write_text(json.dumps(public(), indent=2, ensure_ascii=False), encoding="utf-8")
        files["result"] = str(p)
        artwork_count = len(lv.get("cells", [])) - void_count
        level = {"version": 2 if void_count else 1, "id": level_id, "name": level_id.replace("_", " ").title(),
                 "difficulty": result["difficulty"], "width": lv["width"], "height": lv["height"],
                 "palette": lv["palette"], "cells": lv["cells"]}
        if void_count:
            result["level_metadata"] = {"artworkCellCount": artwork_count, "voidCellCount": void_count}
        lp = out / f"{level_id}.json"
        lp.write_text(json.dumps(level, indent="\t"), encoding="utf-8")
        files["level"] = str(lp)
        cols = result["supply_columns"]
        maxb = max(b["amount"] for col in cols for b in col)
        plan = {"schema": "scrubbots.level_supply_plan.v1", "version": 1, "levelId": level_id,
                "ownerInput": "PixelArtStudio supply pipeline (solver-proven)",
                "ownerInputSha256": hashlib.sha256(json.dumps(cols).encode()).hexdigest(),
                "columnCount": self.rules.column_count, "visiblePreviewDepth": self.rules.preview_depth,
                "maxRobotsPerBatch": maxb,
                "intendedColumnClicks": [s["column"] for s in result["solution_trace"]],
                "columns": [[{"batchId": f"{level_id}-K{ci + 1}-{ri + 1:02d}", "cid": b["color"], "robots": b["amount"]}
                             for ri, b in enumerate(col)] for ci, col in enumerate(cols)]}
        sp = out / f"{level_id}_supply_v1.json"
        sp.write_text(json.dumps(plan, indent="\t"), encoding="utf-8")
        files["supply_plan"] = str(sp)
        result["export_notes"].append(
            "uncapped game contract: maxRobotsPerBatch is a positive per-plan metadata bound; "
            "there is no global batch robot cap.")
        p.write_text(json.dumps(public(), indent=2, ensure_ascii=False), encoding="utf-8")
        return files

