"""Build the attested minimal runtime for one game commit from the local game clone (read-only git).

Usage: python build_runtime.py <commit> <void_anchor> [--apply]
Writes data/Level Factory/Runtime/<commit>/ (new folder only; refuses to overwrite).
"""
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

GAME = r"C:\Users\sekip\Desktop\Scrubbots"
FACTORY = Path(r"C:\Users\sekip\Desktop\Scrubbots - Pixel Art Generator")
OLD = FACTORY / "data" / "Level Factory" / "Runtime" / "aef60a616d4ac401e9dfac15df6fe56e671c0053"
PATTERN = re.compile(r"(?:scripts/.+\.gd|data/(?:config|palettes)/[^/]+\.json)\Z")
DOCS = ["docs/05_TECH_DECISIONS.md", "docs/03_LEVEL_DATA_SPEC.md"]


def git(*args: str, raw: bool = False):
    out = subprocess.run(["git", "-C", GAME, *args], capture_output=True, check=True).stdout
    return out if raw else out.decode().strip()


commit = git("rev-parse", sys.argv[1] + "^{commit}")
anchor = git("rev-parse", sys.argv[2] + "^{commit}")
tree = git("rev-parse", commit + "^{tree}")
target = FACTORY / "data" / "Level Factory" / "Runtime" / commit
if target.exists():
    sys.exit(f"refusing: {target} exists")
subprocess.run(["git", "-C", GAME, "merge-base", "--is-ancestor", anchor, commit], check=True)
subprocess.run(["git", "-C", GAME, "merge-base", "--is-ancestor", commit, "origin/main"], check=True)
ahead = int(git("rev-list", "--count", f"{anchor}..{commit}"))


def entry(path: str, blob: str) -> tuple[dict, bytes]:
    raw = git("cat-file", "blob", blob, raw=True)
    assert hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() == blob
    return {"bytes": len(raw), "git_blob_sha1": blob, "path": path, "sha256": hashlib.sha256(raw).hexdigest()}, raw


files, blobs = [], {}
for line in git("ls-tree", "-r", commit).splitlines():
    meta, path = line.split("\t", 1)
    _mode, kind, blob = meta.split()
    if kind == "blob" and PATTERN.fullmatch(path):
        item, raw = entry(path, blob)
        files.append(item)
        blobs[path] = raw
files.sort(key=lambda item: item["path"])
docs = []
for path in DOCS:
    blob = git("rev-parse", f"{commit}:{path}")
    docs.append(entry(path, blob)[0])
old = json.loads((OLD / "source-attestation.json").read_text(encoding="utf-8"))
manifest = {
    "full_game_checkout_verified": False,
    "installed_owner_source": old["installed_owner_source"],
    "repository": "Sekiph82/Scrubbots",
    "runtime_kind": "LF_PINNED_SOURCE_MINIMAL_RUNTIME",
    "schema": "lf-pinned-game-source-attestation/v1",
    "source_branch": "main",
    "source_commit": commit,
    "source_files": files,
    "source_files_bytes": sum(item["bytes"] for item in files),
    "source_files_count": len(files),
    "source_main_observed_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "tree_entry_count": len(git("ls-tree", "-r", "-t", commit).splitlines()),
    "tree_sha": tree,
    "tree_truncated": False,
    "verified_main_at_task_start": True,
    "void_compare": {"ahead_by": ahead, "behind_by": 0, "merge_base": anchor, "status": "ahead"},
    "void_contract_documents": docs,
}
raw_manifest = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
summary = {
    "commit": commit, "tree": tree, "anchor": anchor, "files": len(files), "bytes": manifest["source_files_bytes"],
    "attestation_sha256": hashlib.sha256(raw_manifest).hexdigest(),
    "project_sha256": hashlib.sha256((OLD / "project.godot").read_bytes()).hexdigest(),
}
print(json.dumps(summary, indent=1))
if "--apply" in sys.argv:
    staging = target.with_name(target.name + ".partial")
    if staging.exists():
        sys.exit(f"refusing: {staging} exists")
    for path, raw in blobs.items():
        out = staging.joinpath(*path.split("/"))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(raw)
    (staging / "project.godot").write_bytes((OLD / "project.godot").read_bytes())
    (staging / "source-attestation.json").write_bytes(raw_manifest)
    staging.rename(target)
    print("written", target)
