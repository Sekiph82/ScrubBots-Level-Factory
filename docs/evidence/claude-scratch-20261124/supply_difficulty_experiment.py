"""Experiment: how far does supply shape move the official Difficulty V1 score?

Runs the pipeline's own solve route (`_run_canonical_artwork_route`) for existing READY
candidates with a forced mean batch size and column count. Pipeline-record writes and
Release Pool entry are disabled in this process, so the pool and statuses never change;
only the route's work folder receives files.
Usage: python supply_difficulty_experiment.py <candidate_id> <mean_batch> <columns>
"""
import json
import sqlite3
import sys
import time
from pathlib import Path

REPO = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator")
sys.path.insert(0, str(REPO / "src"))
from scrubbots_pixel_factory import studio_extensions as s  # noqa: E402
from scrubbots_pixel_factory.supply_pipeline import difficulty_model  # noqa: E402

candidate_id, mean_batch, columns = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
score_band = sys.argv[4] if len(sys.argv) > 4 else None
if mean_batch > 0:
    difficulty_model.DifficultyModel.mean_batch_size = lambda self, image_score, band: mean_batch
captured = {}
s._write_pipeline_record = lambda payload: captured.setdefault("payload", payload)
s.find_candidate = lambda identity: None  # no Release Pool entry

db = sqlite3.connect(f"file:{REPO / 'data/Level Factory/factory.db'}?mode=ro", uri=True)
entry = json.loads(db.execute("select entry_json from release_entries where candidate_id=?", (candidate_id,)).fetchone()[0])
binding = entry["pipeline"].get("owner_source_binding") or {}
bundle = s.read_bundle(s.owner_art_storage.owner_art_paths(s._repository_root())["workspace"] / "Candidates" / candidate_id)
request = {"game_project": str(REPO / "data/Level Factory/Runtime/1de7a7f6cf1b01c8836c1346168976a0c8ae2fbd"),
           "column_count": columns, "solver_timeout_seconds": 900, "real_max_visited": 25000, "candidates": 150, "score_band": score_band, "source_sha256": binding.get("source_sha256"),
           "activity_run_id": f"exp-{candidate_id[16:28]}-m{int(mean_batch)}-c{columns}-{int(time.time())}"}
t = time.time()
payload = s._run_canonical_artwork_route(identity=candidate_id, cells=bundle.artwork.cells, width=bundle.artwork.width,
                                         height=bundle.artwork.height, evidence="supply-difficulty-experiment",
                                         request=request, source_kind="CANDIDATE", owner_source_binding=binding)
primary = payload.get("primary", {})
print(json.dumps({"candidate": candidate_id, "baseline": entry["challenge_score"], "mean_batch": mean_batch, "columns": columns, "score_band": score_band,
                  "disposition": payload.get("disposition"), "score": (primary.get("difficulty") or {}).get("score"),
                  "reason": primary.get("reason"), "seconds": round(time.time() - t)}))
