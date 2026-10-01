"""SupplyExporter: result JSON + (full-canvas only) game LevelData JSON and supply plan
(scrubbots.level_supply_plan.v1, loadable by the game's SupplyPlanLoader)."""
import hashlib
import json
from pathlib import Path


class SupplyExporter:
    def __init__(self, rules):
        self.rules = rules

    def export(self, result, out_dir, level_id):
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        files = {}
        p = out / f"{level_id}_supply_result.json"
        public = lambda: {k: v for k, v in result.items() if not k.startswith("_")}
        p.write_text(json.dumps(public(), indent=2, ensure_ascii=False), encoding="utf-8")
        files["result"] = str(p)
        if not result["image"]["full_canvas"]:
            result["export_notes"].append("transparent pixels: game LevelData has no empty cell, so no "
                                          "level/supply plan files were written (fill the background).")
            p.write_text(json.dumps(public(), indent=2, ensure_ascii=False), encoding="utf-8")
            return files
        lv = result["_level"]
        level = {"version": 1, "id": level_id, "name": level_id.replace("_", " ").title(),
                 "difficulty": result["difficulty"], "width": lv["width"], "height": lv["height"],
                 "palette": lv["palette"], "cells": lv["cells"]}
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

