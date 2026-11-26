"""Add real_play_provenance_v1 records for the already-published levels 201..1000 from Level
Factory's own canonical play, with the exact Send-to-Game code path (game_publisher)."""
import json
import sys
from pathlib import Path

REPO = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator")
GAME = Path(r"C:\Users\sekip\Desktop\ScrubBots")
sys.path.insert(0, str(REPO / "src"))
from scrubbots_pixel_factory.supply_pipeline import game_publisher as gp  # noqa: E402
from scrubbots_pixel_factory.supply_pipeline import release_pool as rp  # noqa: E402

catalog = json.loads((GAME / "data/levels/catalog/production_catalog_v1.json").read_text(encoding="utf-8"))
pool = {e["candidate_id"]: e for e in rp.release_entries()}
records = []
for entry in sorted(catalog["entries"], key=lambda e: e["order"]):
    if entry["order"] <= 200:
        continue
    metadata = json.loads((GAME / entry["metadata_path"].removeprefix("res://")).read_text(encoding="utf-8"))
    pool_entry = pool[entry["id"]]
    assert pool_entry["pipeline_run_id"] == metadata["pipelineRunId"] or pool_entry["pipeline"].get("run_id") == metadata["pipelineRunId"], entry["id"]
    records.append(gp.real_play_record(pool_entry["pipeline"], entry["id"], entry["order"], GAME / entry["supply_plan_path"].removeprefix("res://")))
data = gp._provenance_with(GAME, records)
(GAME / gp.REAL_PLAY_PROVENANCE).write_bytes(data)
print("records added", len(records), "total", len(json.loads(data)["records"]))
