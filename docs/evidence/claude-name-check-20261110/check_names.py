"""Read-only name check for PixelLab rows generated after baseline.json.

For every new job record: Grid atlas exists with the recorded SHA, its 16 slices exist
in Final (56x56, SHA as recorded), and the same Final name is used by the Imported
record and by the Release Pool record. Run from the repository root:
    PYTHONPATH=src python -B docs/evidence/claude-name-check-20261110/check_names.py
"""
import collections
import glob
import hashlib
import json
import os
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
base = json.loads((HERE / "baseline.json").read_text(encoding="utf-8"))
jobs_dir = Path("data/Level Factory/Workspace/Studio Extensions/pixellab-jobs")
tx_dir = Path("data/output/Pixellab/Transactions")
final_dir = Path("data/output/Pixellab/Final")
grid_dir = Path("data/output/Pixellab/Grid Files")
imported_dir = Path("data/Level Factory/Imported")

from scrubbots_pixel_factory.owner_release_library import list_records  # noqa: E402

release = {r["source_id"]: r for r in list_records()["records"]}
tx_by_atlas = {}
for path in tx_dir.glob("pixellab-atlas-*.json"):
    record = json.loads(path.read_text(encoding="utf-8"))
    tx_by_atlas[path.stem.removeprefix("pixellab-atlas-")] = record

new_jobs = []
for path in sorted(jobs_dir.glob("*.json"), key=os.path.getmtime):
    if path.name.endswith(".claim.json") or path.name in base["job_records"]:
        continue
    new_jobs.append(json.loads(path.read_text(encoding="utf-8")))

rows, problems, names_seen = [], [], collections.Counter()
for job in new_jobs:
    atlas_sha = job.get("atlas_sha256")
    row = {"operation_id": job.get("operation_id"), "job_id": job.get("job_id"), "state": job.get("state"),
           "pass": job.get("pass_count"), "grid": None, "finals": [], "issues": []}
    tx = tx_by_atlas.get(atlas_sha or "")
    if not atlas_sha or tx is None:
        row["issues"].append("no atlas/transaction (generation did not finish)")
    else:
        grid = grid_dir / tx["atlas_filename"]
        row["grid"] = grid.name
        if not grid.is_file() or hashlib.sha256(grid.read_bytes()).hexdigest() != atlas_sha:
            row["issues"].append(f"Grid atlas missing or SHA mismatch: {grid.name}")
        if len(tx["slices"]) != 16:
            row["issues"].append(f"{len(tx['slices'])} slices instead of 16")
        for item in tx["slices"]:
            name, sha = item["filename"], item["sha256"]
            names_seen[name] += 1
            row["finals"].append(name)
            final = final_dir / name
            if not final.is_file():
                row["issues"].append(f"{name}: missing in Final"); continue
            raw = final.read_bytes()
            if hashlib.sha256(raw).hexdigest() != sha:
                row["issues"].append(f"{name}: Final SHA mismatch")
            if Image.open(final).size != (56, 56):
                row["issues"].append(f"{name}: not 56x56")
            source_id = "owner-upload-" + sha
            record_dir = imported_dir / source_id
            if record_dir.is_dir():
                meta = json.loads((record_dir / "source.json").read_text(encoding="utf-8"))
                if meta.get("original_filename") != name or not (record_dir / name).is_file():
                    row["issues"].append(f"{name}: Imported name is {meta.get('original_filename')}")
            status = release.get(source_id)
            if status is not None and Path(str(status.get("original_source_path", ""))).name != name:
                row["issues"].append(f"{name}: Release Pool name is {Path(status['original_source_path']).name}")
            if status is None:
                row["issues"].append(f"{name}: not yet in Release Pool (open Level Factory once to sync)")
    rows.append(row)
    problems.extend(f"{row['operation_id']}: {issue}" for issue in row["issues"])

duplicates = [n for n, c in names_seen.items() if c > 1]
sprite_left = ([p.name for p in Path("data/Release Pool").glob("*/sprite-*.png")]
               + [p.name for p in imported_dir.glob("*/sprite-*.png")])
summary = {
    "new_job_records": len(new_jobs),
    "states": dict(collections.Counter(r["state"] for r in rows)),
    "new_final_pngs": sum(len(r["finals"]) for r in rows),
    "duplicate_final_names": duplicates,
    "sprite_named_files_left": sprite_left,
    "rows_with_issues": sum(1 for r in rows if r["issues"]),
    "final_total": len(list(final_dir.glob("*.png"))),
    "grid_total": len(list(grid_dir.glob("*.png"))),
}
(HERE / "result.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1), encoding="utf-8")
print(json.dumps(summary, indent=1))
for line in problems[:60]:
    print("ISSUE", line)
