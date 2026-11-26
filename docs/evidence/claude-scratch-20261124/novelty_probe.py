import sys, statistics
from pathlib import Path
sys.path.insert(0, r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator\src")
from scrubbots_pixel_factory.supply_pipeline import release_pool as rp
from scrubbots_pixel_factory.supply_pipeline.campaign_builder import _similarity
from scrubbots_pixel_factory.supply_pipeline.progression import describe_target
entries = rp.release_entries()
catalog, authority = rp._game_authority(Path(r"C:\Users\sekip\Desktop\ScrubBots"))
tail = authority["_catalog_tail"][-1]
print("tail", {k: tail.get(k) for k in ("order", "challenge_score", "width", "height", "palette", "challenge_vector")})
print("tail sig", tail["signature"])
print("slot201", describe_target(201, authority))
print("cb", authority.get("campaignBuilder"))
sims = [_similarity(tail, e) for e in entries[:2000]]
print("sim vs tail: min %.3f median %.3f max %.3f" % (min(sims), statistics.median(sims), max(sims)))
e = entries[0]; print("entry sig", e.get("signature"), e.get("challenge_vector"), e.get("palette"))
pair = [_similarity(entries[i], entries[i+1]) for i in range(0, 2000, 2)]
print("sim pool pairs: median %.3f min %.3f" % (statistics.median(pair), min(pair)))
