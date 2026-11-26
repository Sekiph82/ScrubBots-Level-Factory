import sys, json
sys.path.insert(0, "src")
from pathlib import Path
from PIL import Image
from scrubbots_pixel_factory.owner_release_library import list_records
recs = list_records()["records"]
ready = [r for r in recs if r.get("status") == "READY"]
print("ready", len(ready))
final = Path("data/output/Pixellab/Final")
idx = {}
import hashlib
for p in final.glob("*.png"):
    idx[hashlib.sha256(p.read_bytes()).hexdigest()] = p
out = []
for r in ready:
    sha = r["source_id"].removeprefix("owner-upload-")
    p = idx.get(sha)
    if not p: continue
    im = Image.open(p).convert("RGBA")
    w, h = im.size
    a = im.getchannel("A")
    corners = [a.getpixel(c) for c in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)]]
    transparent = sum(1 for v in a.getdata() if v == 0)
    if min(corners) > 0 or transparent < w*h*0.05:
        out.append((r["source_id"][:26], p.name, corners, transparent))
for o in out: print(o)
print(len(out))
