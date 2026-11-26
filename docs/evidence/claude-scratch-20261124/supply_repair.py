"""Experiment: repair a LOST real-play supply plan at its jam point (owner idea 2026-11-23).

At the stuck click, shrink the WAITING slot batch holding the most unused robots to the
part it could use, and move the unused robots to a new batch at the end of the same column
(one extra click for that column at the end). Replay; repeat at the new jam point.
Writes only under data/Level Factory/Workspace/claude-supply-repair-experiment/.
"""
import json
import shutil
import sys
from pathlib import Path

REPO = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator")
sys.path.insert(0, str(REPO / "src"))
from scrubbots_pixel_factory.supply_pipeline.real_play_gate import ensure_real_play_gate  # noqa: E402

precheck_dir = Path(sys.argv[1])
out_root = REPO / "data" / "Level Factory" / "Workspace" / "claude-supply-repair-experiment" / sys.argv[2]
rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 8
level_src = next(p for p in precheck_dir.glob("candidate-owner-*.json") if not p.name.endswith(("_supply_v1.json", "_supply_result.json")))
plan = json.loads(next(precheck_dir.glob("*_supply_v1.json")).read_text(encoding="utf-8"))
first = json.loads((precheck_dir / "real_play_result_v2.json").read_text(encoding="utf-8"))
source_sha = first.get("sourceSha256")
result = first
for round_index in range(1, rounds + 1):
    per = result["perDt"]["1/60"]
    if result.get("verdict") != "LOST":
        break
    waiting = [s for s in per["slots"] if s.get("occupied") and s.get("state") == "WAITING" and s.get("remaining", 0) > 0]
    if not waiting:
        print(f"round {round_index}: no WAITING slot to repair"); break
    mode = sys.argv[4] if len(sys.argv) > 4 else "one"
    targets = [max(waiting, key=lambda s: s["remaining"])] if mode == "one" else waiting
    notes = []
    for jam in targets:
        col_index = next(i for i, col in enumerate(plan["columns"]) if any(b["batchId"] == jam["batchId"] for b in col))
        col = plan["columns"][col_index]
        batch = next(b for b in col if b["batchId"] == jam["batchId"])
        used = batch["robots"] - jam["remaining"]
        keep = used if used > 0 else max(1, batch["robots"] // 2)
        moved = batch["robots"] - keep
        if moved <= 0:
            continue
        batch["robots"] = keep
        prefix = jam["batchId"].rsplit("-", 1)[0]
        col.append({"batchId": f"{prefix}-{len(col) + 1:02d}", "cid": batch["cid"], "robots": moved})
        plan["intendedColumnClicks"].append(col_index + 1)
        notes.append(f"{jam['batchId'][-6:]} c{jam['colorId']} {keep + moved}->{keep} (+{moved} K{col_index + 1} end)")
    if not notes:
        print(f"round {round_index}: nothing to shrink"); break
    work = out_root / f"round-{round_index:02d}"
    work.mkdir(parents=True, exist_ok=True)
    level_path = work / level_src.name
    shutil.copyfile(level_src, level_path)
    plan_path = work / (level_src.stem + "_supply_v1.json")
    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    gate = ensure_real_play_gate(level_path, plan_path, work / "real_play_result_v2.json",
                                 source_sha256=source_sha, search_on_loss=False)
    result = gate["result"]
    per = result["perDt"]["1/60"]
    print(f"round {round_index}: {'; '.join(notes)} -> {result.get('verdict')} "
          f"stuck={per.get('stuckClickIndex')}/{len(plan['intendedColumnClicks'])} residue={per.get('final', {}).get('boardResidue')}",
          flush=True)
print("final:", result.get("verdict"))
