import sys, json, hashlib, importlib.util
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "level_factory/scripts"))
from scrubbots_pixel_factory.owner_release_library import list_records, transition
spec = importlib.util.spec_from_file_location("launcher", ROOT / "level_factory/scripts/factory_core_launcher.py")
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
names = [f"LF-{n:06d}.png" for n in range(1297, 1313)] + ["LF-001213.png"]
final = ROOT / "data/output/Pixellab/Final"
targets = []
for n in names:
    p = final / n
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    targets.append({"file": n, "sha256": sha, "source_id": f"owner-upload-{sha}"})
ready = {r["source_id"] for r in list_records("READY")["records"]}
assert all(t["source_id"] in ready for t in targets), [t for t in targets if t["source_id"] not in ready]
ev = ROOT / "docs/evidence/claude-reject-arctic-tornado-20261122"; ev.mkdir(parents=True, exist_ok=True)
(ev / "before-manifest.json").write_text(json.dumps({"at": datetime.now(timezone.utc).isoformat(), "targets": targets}, indent=2))
if "--apply" not in sys.argv: print("dry", len(targets)); sys.exit()
for t in targets:
    reason = "Owner 2026-11-22: tornado image disliked; remove from the system." if t["file"] == "LF-001213.png" else "Owner 2026-11-22: opaque white background is not OK for READY."
    transition(t["source_id"], "REJECTED", source_sha256=t["sha256"], provider="PIXELLAB", original_source_path=str((final / t["file"]).resolve()), reason=reason, evidence={"owner_review": "release-pool-screenshots-20261122"})
result = L._purge_rejected_sources([t["source_id"] for t in targets])
(ev / "purge-result.json").write_text(json.dumps(result, indent=2))
print(result["purged"], result["skipped"], len(result["deleted"]))
print(list_records()["counts"])
