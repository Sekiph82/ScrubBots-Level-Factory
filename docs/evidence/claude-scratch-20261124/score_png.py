"""Official Difficulty V1 score of one PNG through the pipeline route, without any pool/status write.
Usage: python score_png.py <png> <name>"""
import hashlib
import json
import sys
import time
from pathlib import Path

from PIL import Image

REPO = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator")
sys.path.insert(0, str(REPO / "src"))
from scrubbots_pixel_factory import CANONICAL_PALETTE  # noqa: E402
from scrubbots_pixel_factory import studio_extensions as s  # noqa: E402

png, name = Path(sys.argv[1]), sys.argv[2]
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
by_hex = {c.hex.upper(): c.id for c in CANONICAL_PALETTE.colors}
img = Image.open(png).convert("RGBA")
cells = []
for r, g, b, a in img.getdata():
    cells.append("VOID" if a == 0 else by_hex[f"#{r:02X}{g:02X}{b:02X}"])
sha = hashlib.sha256(png.read_bytes()).hexdigest()
s._write_pipeline_record = lambda payload: None
s.find_candidate = lambda identity: None
identity = f"candidate-pxl-trial-{name.replace('_', '-')}"
request = {"game_project": str(REPO / "data/Level Factory/Runtime/1de7a7f6cf1b01c8836c1346168976a0c8ae2fbd"),
           "column_count": 3, "solver_timeout_seconds": 900, "real_max_visited": 25000, "candidates": 48,
           "source_sha256": sha, "seed": seed, "activity_run_id": f"pxl-{name}-{int(time.time())}"}
t = time.time()
payload = s._run_canonical_artwork_route(identity=identity, cells=cells, width=img.width, height=img.height,
                                         evidence="pxl-difficulty-trial", request=request, source_kind="CANDIDATE")
primary = payload.get("primary", {})
print(json.dumps({"name": name, "seed": seed, "colors": len(set(cells) - {"VOID"}), "cells": sum(c != "VOID" for c in cells),
                  "disposition": payload.get("disposition"), "score": (primary.get("difficulty") or {}).get("score"),
                  "vector": (primary.get("result") or {}).get("solver_metrics", {}).get("official_difficulty_v1", {}).get("vector"),
                  "reason": primary.get("reason"), "seconds": round(time.time() - t)}))
