"""Read-only timing of the campaign planner on the real pool (no game or pool writes)."""
import sys
import time
from pathlib import Path

REPO = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator")
sys.path.insert(0, str(REPO / "src"))
from scrubbots_pixel_factory.supply_pipeline import release_pool as rp  # noqa: E402
from scrubbots_pixel_factory.supply_pipeline.campaign_builder import build_campaign_plan  # noqa: E402

k = int(sys.argv[1])
t = time.time()
entries = rp.release_entries()
print("entries", len(entries), round(time.time() - t, 1), "s", flush=True)
import collections
print(collections.Counter(e.get("eligibility_source") for e in entries))
print("unique", len({e["candidate_id"] for e in entries}))
catalog, authority = rp._game_authority(Path(r"C:\Users\sekip\Desktop\ScrubBots"))
t = time.time()
plan = build_campaign_plan(catalog=catalog, authority=authority, pool=entries, k=k)
print("plan k", k, round(time.time() - t, 1), "s; filled", sum(r["chosen_id"] is not None for r in plan["slots"]),
      "prefix", len(plan["publishable_prefix"]), "shortages", len(plan["shortages"]))
print(collections.Counter(r["class"] for r in plan["slots"] if r["chosen_id"]))
import json
print(json.dumps(plan["shortages"][:1], indent=1)[:2500])
print(json.dumps(plan["slots"][0], indent=1)[:800])
print("envelope", authority["_production_envelope"])
e = entries[0]
print({k: e.get(k) for k in ("width", "height", "challenge_score", "dominant_profile")}, len(set(e.get("used_colors", e.get("palette", [])))))
