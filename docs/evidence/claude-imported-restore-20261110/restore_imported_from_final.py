"""Re-register data/Level Factory/Imported from PixelLab Final (2026-11-10 incident).

tests/unit/test_sb_lfx_014_batch_import.py deleted every owner-upload-* folder in
the real Imported store. Every Release Pool record is backed by a Final PNG with
the identical SHA-256, so each record is rebuilt with the same canonical
import_owner_upload() call the app runs on startup. Additive only: it never
deletes, never touches Final, Grid Files or Release Pool. Run from repo root:
    PYTHONPATH=src python -B docs/evidence/claude-imported-restore-20261110/restore_imported_from_final.py
"""
import collections
import datetime
import hashlib
import json
from pathlib import Path

from scrubbots_pixel_factory.owner_upload import import_owner_upload, owner_upload_root
from scrubbots_pixel_factory.owner_release_library import list_records

HERE = Path(__file__).resolve().parent
final_dir = Path("data/output/Pixellab/Final")
imported = owner_upload_root()
before = sorted(p.name for p in imported.iterdir())
release = {r["source_id"]: r for r in list_records()["records"]}

results, states = [], collections.Counter()
for png in sorted(final_dir.glob("*.png")):
    sha = hashlib.sha256(png.read_bytes()).hexdigest()
    outcome = import_owner_upload(png)
    states[outcome.get("state")] += 1
    record_dir = imported / f"owner-upload-{sha}"
    stored = record_dir / png.name
    results.append({
        "final": png.name, "sha256": sha, "state": outcome.get("state"), "error": outcome.get("error"),
        "stored_sha256": hashlib.sha256(stored.read_bytes()).hexdigest() if stored.is_file() else None,
        "source_json_sha256": hashlib.sha256((record_dir / "source.json").read_bytes()).hexdigest() if (record_dir / "source.json").is_file() else None,
        "release_status": (release.get(f"owner-upload-{sha}") or {}).get("status"),
    })

after = sorted(p.name for p in imported.iterdir())
summary = {
    "ran_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "imported_before": len(before), "imported_after": len(after), "final_pngs": len(results),
    "states": dict(states),
    "byte_mismatches": [r["final"] for r in results if r["stored_sha256"] != r["sha256"]],
    "release_records_without_imported": sorted(set(release) - set(after)),
}
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
(HERE / f"restore-result-{stamp}.json").write_text(json.dumps({"summary": summary, "items": results}, indent=1), encoding="utf-8")
print(json.dumps(summary, indent=1))
