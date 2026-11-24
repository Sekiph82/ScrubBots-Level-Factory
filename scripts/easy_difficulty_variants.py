"""EASY difficulty variants of READY levels (owner decision 2026-11-24).

The 1000-level campaign needs 600 EASY levels (official score < 43.9) but the pool has
about that many. An experiment showed small robot batches lower the official Difficulty
V1 score by ~2-10 points. For each READY level scoring in [--min, --max) this tool
re-solves it through the unchanged pipeline route with ``mean_batch`` small batches,
trying 3 then 5 columns. Only a READY result below the EASY band edge is kept: its
pipeline record is written and it enters the Release Pool, where the newest READY run of
a level is the one listed. A result that misses EASY writes nothing.

Usage: python -B scripts/easy_difficulty_variants.py --limit 600 --workers 6 [--dry-run]
Results append to data/Level Factory/Workspace/easy-variants/results.jsonl.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

EASY_MAX = 43.9
VARIANTS = ((7.0, 3), (7.0, 5))
RUNTIME = REPO / "data" / "Level Factory" / "Runtime" / "1de7a7f6cf1b01c8836c1346168976a0c8ae2fbd"


def _solve_variant(candidate_id: str, mean_batch: float, columns: int, keep_below: float, dry_run: bool) -> dict:
    from scrubbots_pixel_factory import studio_extensions as s

    db = sqlite3.connect(f"file:{REPO / 'data/Level Factory/factory.db'}?mode=ro", uri=True)
    rows = [json.loads(t) for (t,) in db.execute("select entry_json from release_entries where candidate_id=?", (candidate_id,))]
    entry = max(rows, key=lambda e: str(e.get("pipeline", {}).get("created_at", "")))
    binding = entry["pipeline"].get("owner_source_binding") or {}
    bundle = s.read_bundle(s.owner_art_storage.owner_art_paths(s._repository_root())["workspace"] / "Candidates" / candidate_id)
    request = {"game_project": str(RUNTIME), "column_count": columns, "mean_batch": mean_batch,
               "difficulty_variant": "EASY", "solver_timeout_seconds": 900, "real_max_visited": 25000, "candidates": 48,
               "source_sha256": binding.get("source_sha256"),
               "activity_run_id": f"easy-{candidate_id[16:28]}-m{int(mean_batch)}-c{columns}-{int(time.time())}"}
    write_record, find = s._write_pipeline_record, s.find_candidate
    captured: dict = {}
    s._write_pipeline_record = lambda payload: captured.setdefault("payload", payload)
    s.find_candidate = lambda identity: None
    started = time.time()
    try:
        payload = s._run_canonical_artwork_route(identity=candidate_id, cells=bundle.artwork.cells, width=bundle.artwork.width,
                                                 height=bundle.artwork.height, evidence="easy-difficulty-variant",
                                                 request=request, source_kind="CANDIDATE", owner_source_binding=binding)
    finally:
        s._write_pipeline_record, s.find_candidate = write_record, find
    score = ((payload.get("primary") or {}).get("difficulty") or {}).get("score")
    kept = payload.get("disposition") == "READY" and isinstance(score, (int, float)) and score < keep_below
    pool = None
    if kept and not dry_run:
        write_record(payload)
        candidate = find(candidate_id)
        pool = s._enter_candidate_release_pool(candidate, pipeline=payload).get("disposition") if candidate else "CANDIDATE_NOT_FOUND"
    return {"candidate": candidate_id, "baseline": entry["challenge_score"], "mean_batch": mean_batch, "columns": columns,
            "disposition": payload.get("disposition"), "score": score, "kept": kept, "pool": pool,
            "reason": (payload.get("primary") or {}).get("reason"), "seconds": round(time.time() - started)}


def _candidate(candidate_id: str, keep_below: float, dry_run: bool, variants=VARIANTS) -> list[dict]:
    results = []
    for mean_batch, columns in variants:
        try:
            result = _solve_variant(candidate_id, mean_batch, columns, keep_below, dry_run)
        except Exception as exc:  # one level must not stop the run
            result = {"candidate": candidate_id, "mean_batch": mean_batch, "columns": columns, "error": str(exc)[:400]}
        results.append(result)
        if result.get("kept"):
            break
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min", type=float, default=EASY_MAX)
    parser.add_argument("--max", type=float, default=48.0)
    parser.add_argument("--limit", type=int, default=600)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--keep-below", type=float, default=EASY_MAX,
                        help="keep a re-solve only below this score (43.9 = EASY, 52.4 = MEDIUM or easier)")
    parser.add_argument("--variants", default="7:3,7:5", help="mean_batch:columns tried in order until one is kept")
    parser.add_argument("--results", default="results.jsonl")
    args = parser.parse_args()
    variants = tuple((float(m), int(c)) for m, c in (item.split(":") for item in args.variants.split(",")))
    db = sqlite3.connect(f"file:{REPO / 'data/Level Factory/factory.db'}?mode=ro", uri=True)
    from scrubbots_pixel_factory import factory_db
    pool = factory_db.release_entry_rows(db)
    targets = sorted((e for e in pool if args.min <= float(e["challenge_score"]) < args.max), key=lambda e: e["challenge_score"])
    out_dir = REPO / "data" / "Level Factory" / "Workspace" / "easy-variants"
    out_dir.mkdir(parents=True, exist_ok=True)
    done = set()
    results_path = out_dir / args.results
    if results_path.is_file():
        done = {json.loads(line)["candidate"] for line in results_path.read_text(encoding="utf-8").splitlines() if line.strip()}
    queue = [e["candidate_id"] for e in targets if e["candidate_id"] not in done][: args.limit]
    print(f"{len(targets)} levels in [{args.min}, {args.max}); {len(queue)} queued", flush=True)
    with ProcessPoolExecutor(args.workers) as pool_executor, results_path.open("a", encoding="utf-8") as out:
        for results in pool_executor.map(_candidate, queue, [args.keep_below] * len(queue), [args.dry_run] * len(queue),
                                         [variants] * len(queue)):
            for result in results:
                out.write(json.dumps(result) + "\n")
            out.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
