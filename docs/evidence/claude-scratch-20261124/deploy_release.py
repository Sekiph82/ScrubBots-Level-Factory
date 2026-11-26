"""Bounded Release deploy: tracked code under src/, level_factory/scripts, level_factory/scenes.

Dry run by default; --apply backs up every replaced file first and writes
.claude-deployed-commit. Never touches data/, output/ or any untracked path.
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator")
RELEASE = REPO / "Release" / "ScrubBots Factory Studio"
SCOPES = ("src/", "level_factory/scripts/", "level_factory/scenes/")
apply = "--apply" in sys.argv

head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
tracked = subprocess.run(["git", "-C", str(REPO), "ls-files", *SCOPES], capture_output=True, text=True, check=True).stdout.split("\n")


def norm(raw: bytes) -> bytes:
    return raw.replace(b"\r\n", b"\n")


changes = []
for rel in filter(None, tracked):
    blob = subprocess.run(["git", "-C", str(REPO), "show", f"HEAD:{rel}"], capture_output=True, check=True).stdout
    target = RELEASE / rel
    if target.exists() and norm(target.read_bytes()) == norm(blob):
        continue
    changes.append((rel, blob, "NEW" if not target.exists() else "CHANGED"))

for rel, _, kind in changes:
    print(kind, rel)
print(f"{len(changes)} files differ from HEAD {head[:8]}")
if apply and changes:
    backup = RELEASE.parent / ".claude-deploy-backup-20261112" / f"pre-{head[:8]}"
    manifest = []
    for rel, blob, kind in changes:
        target = RELEASE / rel
        if target.exists():
            saved = backup / rel
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
        manifest.append({"path": rel, "kind": kind, "sha256": hashlib.sha256(blob).hexdigest()})
    (backup / "deploy-manifest.json").parent.mkdir(parents=True, exist_ok=True)
    (backup / "deploy-manifest.json").write_text(json.dumps({"commit": head, "files": manifest}, indent=1), encoding="utf-8")
    (RELEASE / ".claude-deployed-commit").write_text(head + "\n", encoding="utf-8")
    print("applied; backups in", backup)
