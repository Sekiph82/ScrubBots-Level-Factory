import sys, json
from pathlib import Path
sys.path.insert(0, "src")
from scrubbots_pixel_factory.supply_pipeline import release_pool
from scrubbots_pixel_factory.owner_release_library import list_records
ev = Path("docs/evidence/claude-reject-arctic-tornado-20261122")
targets = json.loads((ev / "before-manifest.json").read_text())["targets"]
statuses = {r["source_id"] for r in list_records()["records"]}
cids = [f"candidate-owner-{t['sha256'][:48]}" for t in targets]
assert not any(t["source_id"] in statuses for t in targets), "a target still has a status"
before = len(release_pool.slim_release_entries())
deleted = []
if "--apply" in sys.argv:
    for cid in cids: deleted += release_pool.purge_candidate_entries(cid)
    (ev / "release-entries-purge.json").write_text(json.dumps({"deleted": deleted}, indent=2))
print("pool before", before, "after", len(release_pool.slim_release_entries()), "deleted", len(deleted))
