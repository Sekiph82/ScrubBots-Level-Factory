"""Owner-approved (2026-11-10) removal of batch-import ledgers written into the
real data/Level Factory/Batches/Imports by unisolated unit tests.

A ledger is removed only when ALL hold: no item SHA matches a PixelLab Final
PNG, every item filename is the synthetic test name same.png, and its
source_folder is one of the test folder labels. The manifest (name, size,
SHA-256 of the ledger bytes) is written before anything is removed.
"""
import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEST_FOLDERS = {"approved", "other-approved-folder"}
final = {hashlib.sha256(p.read_bytes()).hexdigest() for p in Path("data/output/Pixellab/Final").glob("*.png")}
root = Path("data/Level Factory/Batches/Imports").resolve()
selected = []
for path in sorted(root.glob("batch-import-*.json")):
    raw = path.read_bytes()
    value = json.loads(raw.decode("utf-8"))
    items = value.get("items", [])
    shas = {i.get("source_sha256") for i in items if i.get("source_sha256")}
    names = {Path(str(i.get("original_source_path") or i.get("filename") or "")).name for i in items}
    if items and shas and not (shas & final) and names == {"same.png"} and value.get("source_folder") in TEST_FOLDERS:
        assert path.resolve().parent == root
        selected.append({"name": path.name, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                         "source_folder": value.get("source_folder"), "item_sha256": sorted(shas)})
stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
(HERE / f"deleted-ledgers-{stamp}.json").write_text(json.dumps({"count": len(selected), "ledgers": selected}, indent=1), encoding="utf-8")
for item in selected:
    (root / item["name"]).unlink()
remaining = len(list(root.glob("batch-import-*.json")))
print(json.dumps({"deleted": len(selected), "remaining_ledgers": remaining}))
