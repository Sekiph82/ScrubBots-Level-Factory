"""Dry run of the Studio 'Send to Game' path into a throw-away clone of the game.

Clones the owner's game checkout (committed state only), points the clone at the canonical
origin URL, then runs the exact Studio backend: build_release_plan + approve_release_plan.
The owner's game folder and the Studio plan file are never written (plan goes to a temp
extensions root).
Usage: python dry_run_game_release.py <count>
"""
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator")
GAME = Path(r"C:\Users\sekip\Desktop\ScrubBots")
sys.path.insert(0, str(REPO / "src"))
from scrubbots_pixel_factory import studio_extensions as studio  # noqa: E402
from scrubbots_pixel_factory.supply_pipeline import release_pool as rp  # noqa: E402

count = int(sys.argv[1])
work = Path(tempfile.mkdtemp(prefix="game-release-dry-"))
clone = work / "ScrubBots"
git = lambda *a: subprocess.run(["git", "-C", str(clone), *a], check=True, capture_output=True, text=True).stdout.strip()
subprocess.run(["git", "clone", "--quiet", "--no-hardlinks", str(GAME), str(clone)], check=True)
git("remote", "set-url", "origin", "https://github.com/Sekiph82/Scrubbots.git")
git("update-ref", "refs/remotes/origin/main", git("rev-parse", "HEAD"))
ext = work / "extensions"
studio.extensions_root = lambda: ext  # plan file goes to the temp root, not the Studio one
t = time.time()
plan = rp.build_release_plan(game_project=clone, k=count)
print("plan", len(plan["publishable_prefix"]), "slots in", round(time.time() - t), "s", flush=True)
t = time.time()
result = rp.approve_release_plan(plan_hash=plan["plan_hash"], game_project=clone)
orders = result.get("orders", [])
print("PUBLISHED", len(orders), orders[:1], orders[-1:], "in", round(time.time() - t), "s", flush=True)
catalog = json.loads((clone / "data/levels/catalog/production_catalog_v1.json").read_text(encoding="utf-8"))
print("clone catalog entries", len(catalog["entries"]), "work dir", work)
