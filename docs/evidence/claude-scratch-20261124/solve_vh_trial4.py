"""Solve only the 16 VERY_HARD trial PNGs (LF-006379..006394) through the installed Studio backend."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator")
LAUNCHER = REPO / "Release" / "ScrubBots Factory Studio" / "level_factory" / "scripts" / "factory_core_launcher.py"
SCRATCH = Path(__file__).parent


def op(name, request):
    path = SCRATCH / f"vh_{name}.json"
    path.write_text(json.dumps(request), encoding="utf-8")
    out = subprocess.run([sys.executable, "-B", str(LAUNCHER), "studio-extension", "--operation", name, "--request-file", str(path)],
                         capture_output=True, text=True, cwd=LAUNCHER.parents[2])
    line = [l for l in out.stdout.splitlines() if l.strip().startswith("{")][-1]
    data = json.loads(line)
    return data.get("payload", data)


ids = ["owner-upload-" + hashlib.sha256((REPO / f"data/output/Pixellab/Final/LF-{n:06d}.png").read_bytes()).hexdigest() for n in range(6427, 6443)]
composite = op("pending-png-batch-create", {"source_ids": ids})
batch_id = composite.get("batch_id")
print("composite", batch_id, flush=True)
settings = {"game_project": str(REPO / "data" / "Level Factory" / "Runtime" / "1de7a7f6cf1b01c8836c1346168976a0c8ae2fbd"),
            "background_intent": "TRANSPARENT", "solver_timeout_seconds": 900}
created = op("png-batch-create", {"batch_id": batch_id, "settings": settings})
job = created.get("job", {})
print("job", job.get("job_id"), "items", len(job.get("items", [])), created.get("disposition"), flush=True)
ran = op("png-batch-run", {"job_id": job["job_id"], "expected_batch_id": batch_id})
print("run", ran.get("state"), ran.get("disposition"), (ran.get("job") or {}).get("counts"), flush=True)
