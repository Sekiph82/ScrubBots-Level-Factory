#!/usr/bin/env python3
"""Owner-authorized, SHA-guarded LF/RP reset and PixelLab stable-name migration.

Dry-run is read-only. Apply requires the exact dry-run plan digest. The reset
deletes only data/Release Pool, data/Level Factory, the old explicitly named LF
recovery archive/manifest, and non-protected PNG files elsewhere under data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
from typing import Any

from PIL import Image


PROTECTED = ("retained-game-levels", "input", "palette")
FINAL_REL = Path("output/Pixellab/Final")
GRID_REL = Path("output/Pixellab/Grid Files")
PIXELLAB_REL = Path("output/Pixellab")
LEVEL_FACTORY_REL = Path("Level Factory")
RELEASE_POOL_REL = Path("Release Pool")
LEGACY_ARCHIVE_REL = Path("legacy-level-cleanup-recovery-archive")
LEGACY_MANIFEST_REL = Path("legacy-level-cleanup-manifest.json")
NAME_MANIFEST = "asset-name-manifest.json"


class ResetError(RuntimeError):
    pass


def digest_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def reject_reparse(path: Path) -> None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400):
        raise ResetError(f"refusing symlink/reparse path: {path}")
    is_junction = getattr(path, "is_junction", None)
    if callable(is_junction) and is_junction():
        raise ResetError(f"refusing junction path: {path}")


def walk_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    reject_reparse(root)
    result: list[Path] = []
    for current, dirs, names in os.walk(root, topdown=True, followlinks=False):
        base = Path(current)
        for name in list(dirs):
            child = base / name
            reject_reparse(child)
            if child.is_symlink() or not child.is_dir():
                raise ResetError(f"unexpected non-directory in tree: {child}")
        for name in names:
            child = base / name
            reject_reparse(child)
            if not child.is_file():
                raise ResetError(f"unexpected non-file in tree: {child}")
            result.append(child)
    return sorted(result, key=lambda p: p.as_posix().casefold())


def file_inventory(root: Path, files: list[Path] | None = None) -> list[dict[str, Any]]:
    selected = files if files is not None else walk_files(root)
    result = []
    for path in selected:
        raw = path.read_bytes()
        result.append({"path": path.relative_to(root).as_posix(), "sha256": digest_bytes(raw), "bytes": len(raw)})
    return result


def rgba(path: Path) -> tuple[tuple[int, int], bytes]:
    try:
        with Image.open(path) as image:
            if image.format != "PNG":
                raise ResetError(f"PNG extension/content mismatch: {path}")
            image.verify()
        with Image.open(path) as image:
            converted = image.convert("RGBA")
            return converted.size, converted.tobytes()
    except ResetError:
        raise
    except Exception as exc:
        raise ResetError(f"PNG validation failed: {path}: {type(exc).__name__}") from exc


def source_files(data: Path, rel: Path) -> list[Path]:
    root = data / rel
    if not root.is_dir():
        raise ResetError(f"required PixelLab source folder is missing: {root}")
    files = walk_files(root)
    if any(path.suffix.lower() != ".png" for path in files):
        raise ResetError(f"unexpected non-PNG file in PixelLab source folder: {root}")
    return files


def protected_snapshots(data: Path) -> dict[str, list[dict[str, Any]]]:
    result = {}
    for name in PROTECTED:
        folder = data / name
        if not folder.is_dir():
            raise ResetError(f"protected owner folder is missing: {folder}")
        result[name] = file_inventory(folder)
    return result


def mapped_pixel_art(final_files: list[Path], grid_files: list[Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sprite_by_pixels: dict[tuple[int, str], list[dict[str, Any]]] = {}
    for sprite in final_files:
        (width, height), pixels = rgba(sprite)
        if not (51 <= width <= 59 and 51 <= height <= 59):
            raise ResetError(f"Final PNG dimensions outside supported range: {sprite.name} {(width, height)}")
        record = {"source": sprite, "old_name": sprite.name, "sha256": digest_bytes(sprite.read_bytes()), "dimensions": [width, height]}
        key = ((width, height), digest_bytes(pixels))
        sprite_by_pixels.setdefault(key, []).append(record)

    atlases: list[dict[str, Any]] = []
    sprites: list[dict[str, Any]] = []
    atlas_rows: list[tuple[str, Path, str, tuple[int, int], list[dict[str, Any]]]] = []
    for atlas in grid_files:
        (width, height), _ = rgba(atlas)
        if width % 4 or height % 4 or not (51 <= width // 4 <= 59 and 51 <= height // 4 <= 59):
            raise ResetError(f"Grid atlas does not have a valid 4x4 51..59 geometry: {atlas.name} {(width, height)}")
        atlas_sha = digest_bytes(atlas.read_bytes())
        with Image.open(atlas) as image:
            sheet = image.convert("RGBA")
        frame_w, frame_h = sheet.width // 4, sheet.height // 4
        cells: list[dict[str, Any]] = []
        for index in range(1, 17):
            x, y = ((index - 1) % 4) * frame_w, ((index - 1) // 4) * frame_h
            cell = sheet.crop((x, y, x + frame_w, y + frame_h))
            matches = sprite_by_pixels.get(((frame_w, frame_h), digest_bytes(cell.tobytes())), [])
            if len(matches) != 1:
                raise ResetError(f"atlas {atlas.name} frame {index} has {len(matches)} exact Final PNG matches")
            source = matches[0]
            if any(item["source"] == source["source"] for item in cells):
                raise ResetError(f"one Final PNG matches more than one cell in atlas {atlas.name}")
            cell_record = {**source, "index": index}
            cells.append(cell_record)
        atlas_rows.append((atlas_sha, atlas, atlas.name, (width, height), cells))

    atlas_rows.sort(key=lambda item: (item[0], item[2].casefold(), item[2]))
    final_seen: set[Path] = set()
    for atlas_number, (atlas_sha, atlas, old_name, dimensions, cells) in enumerate(atlas_rows, 1):
        atlas_name = f"PX-ATLAS-{atlas_number:06d}.png"
        atlases.append({"sha256": atlas_sha, "source": atlas, "original_filename": old_name,
                        "filename": atlas_name, "dimensions": list(dimensions), "frame_dimensions": [dimensions[0] // 4, dimensions[1] // 4]})
        for cell in cells:
            if cell["source"] in final_seen:
                raise ResetError(f"Final PNG is matched to multiple atlas cells: {cell['old_name']}")
            final_seen.add(cell["source"])
            sprite_number = len(sprites) + 1
            sprites.append({"sha256": cell["sha256"], "source": cell["source"], "original_filename": cell["old_name"],
                            "filename": f"LF-{sprite_number:06d}.png", "dimensions": cell["dimensions"],
                            "atlas_sha256": atlas_sha, "atlas_filename": atlas_name, "index": cell["index"]})
    if len(final_seen) != len(final_files):
        missing = sorted(p.name for p in set(final_files) - final_seen)
        raise ResetError(f"{len(missing)} Final PNG(s) are not mapped to exactly one atlas cell: {missing[:4]}")
    return atlases, sprites


def migrations_from_release(data: Path, atlases: list[dict[str, Any]], sprites: list[dict[str, Any]]) -> list[dict[str, Any]]:
    atlas_by_sha = {item["sha256"]: item for item in atlases}
    sprite_by_pair = {(item["atlas_sha256"], item["index"]): item for item in sprites}
    pending = data / RELEASE_POOL_REL / "Pending"
    migrations = []
    if not pending.exists():
        return migrations
    for path in sorted(pending.glob("pixellab-atlas-*.json"), key=lambda item: item.name):
        if path.is_symlink() or not path.is_file():
            raise ResetError(f"PixelLab transaction file is unsafe: {path}")
        value = json.loads(path.read_text(encoding="utf-8"))
        atlas_sha = value.get("source_atlas_sha256") if isinstance(value, dict) else None
        if (not isinstance(value, dict) or value.get("schema") != "scrubbots-pixellab-atlas-transaction/v1"
                or value.get("state") != "FINALIZED" or atlas_sha not in atlas_by_sha
                or len(value.get("slices", [])) != 16):
            raise ResetError(f"existing PixelLab transaction cannot be verified: {path.name}")
        atlas_record = atlas_by_sha[atlas_sha]
        if value.get("atlas_filename") != atlas_record["original_filename"]:
            raise ResetError(f"existing atlas transaction filename mismatch: {path.name}")
        rows = []
        for row in value["slices"]:
            match = sprite_by_pair.get((atlas_sha, row.get("index")))
            if (match is None or row.get("filename") != match["original_filename"] or row.get("sha256") != match["sha256"]):
                raise ResetError(f"existing atlas transaction slice mismatch: {path.name}")
            rows.append({"index": match["index"], "sha256": match["sha256"], "filename": match["filename"]})
        rewritten = dict(value)
        rewritten.update({"schema": "scrubbots-pixellab-atlas-transaction/v1", "state": "FINALIZED",
                          "atlas_filename": atlas_record["filename"], "slices": sorted(rows, key=lambda row: row["index"])})
        migrations.append({"source": path.relative_to(data).as_posix(), "destination": f"output/Pixellab/Transactions/{path.name}",
                           "sha256": digest_bytes(canonical_json(rewritten)), "document": rewritten})
    return migrations


def build_plan(repository: Path) -> dict[str, Any]:
    repository = repository.resolve(strict=True)
    if not ((repository / "TASKS.md").is_file() and ((repository / ".git").is_dir() or (repository / ".git").is_file())):
        raise ResetError("run only from the canonical task-authorized Desktop checkout")
    data = repository / "data"
    if not data.is_dir():
        raise ResetError("canonical data directory is missing")
    reject_reparse(data)
    for name in PROTECTED:
        reject_reparse(data / name)
    protected = protected_snapshots(data)
    final_files = source_files(data, FINAL_REL)
    grid_files = source_files(data, GRID_REL)
    if len(final_files) != 304 or len(grid_files) != 19:
        raise ResetError(f"expected 304 Final and 19 Grid PNGs, found {len(final_files)} and {len(grid_files)}")
    atlases, sprites = mapped_pixel_art(final_files, grid_files)

    removals: dict[str, dict[str, Any]] = {}
    for rel in (RELEASE_POOL_REL, LEVEL_FACTORY_REL, LEGACY_ARCHIVE_REL):
        root = data / rel
        for path in walk_files(root):
            removals[path.relative_to(data).as_posix()] = {"sha256": digest_bytes(path.read_bytes()), "bytes": path.stat().st_size}
    legacy_manifest = data / LEGACY_MANIFEST_REL
    if legacy_manifest.exists():
        reject_reparse(legacy_manifest)
        if not legacy_manifest.is_file():
            raise ResetError("legacy cleanup manifest is not a regular file")
        removals[LEGACY_MANIFEST_REL.as_posix()] = {"sha256": digest_bytes(legacy_manifest.read_bytes()), "bytes": legacy_manifest.stat().st_size}

    keep_roots = [data / name for name in PROTECTED] + [data / FINAL_REL, data / GRID_REL]
    for path in walk_files(data):
        if path.suffix.lower() != ".png" or any(path == root or root in path.parents for root in keep_roots):
            continue
        removals[path.relative_to(data).as_posix()] = {"sha256": digest_bytes(path.read_bytes()), "bytes": path.stat().st_size}

    transactions = migrations_from_release(data, atlases, sprites)
    existing_manifest = data / PIXELLAB_REL / NAME_MANIFEST
    original_name_map = None
    if existing_manifest.is_file():
        original_name_map = json.loads(existing_manifest.read_text(encoding="utf-8"))
        if not isinstance(original_name_map, dict) or original_name_map.get("schema") != "scrubbots-pixellab-asset-names/v1":
            raise ResetError("existing PixelLab stable-name manifest has an unknown schema")
    name_manifest = {
        "schema": "scrubbots-pixellab-asset-names/v1", "version": 1, "migration_state": "COMPLETE",
        "migration_basis": "EXACT_DECODED_RGBA_PIXEL_MATCH", "atlas_match_count": len(atlases),
        "sprite_match_count": len(sprites),
        "atlases": {item["sha256"]: {"filename": item["filename"], "sha256": item["sha256"],
                       "original_filename": item["original_filename"], "dimensions": item["dimensions"],
                       "migration_basis": "EXACT_DECODED_RGBA_PIXEL_MATCH"} for item in atlases},
        "sprites": {f"{item['atlas_sha256']}:{item['index']:02d}": {"filename": item["filename"], "sha256": item["sha256"],
                       "atlas_sha256": item["atlas_sha256"], "index": item["index"],
                       "original_filename": item["original_filename"], "dimensions": item["dimensions"],
                       "migration_basis": "EXACT_DECODED_RGBA_PIXEL_MATCH"} for item in sprites},
    }
    if original_name_map:
        # Preserve preexisting original-name metadata if this is an interrupted rerun.
        for sha, record in name_manifest["atlases"].items():
            old = original_name_map.get("atlases", {}).get(sha, {})
            if isinstance(old, dict) and old.get("original_filename"):
                record["original_filename"] = old["original_filename"]
        for key, record in name_manifest["sprites"].items():
            old = original_name_map.get("sprites", {}).get(key, {})
            if isinstance(old, dict) and old.get("original_filename"):
                record["original_filename"] = old["original_filename"]

    protected_after_expectation = protected
    plan = {
        "schema": "scrubbots-lf-rp-reset-plan/v1", "repository": str(repository),
        "protected": protected, "remove": removals,
        "final": [{"old": item["source"].relative_to(data).as_posix(), "new": (data / FINAL_REL / item["filename"]).relative_to(data).as_posix(), "sha256": item["sha256"]} for item in sprites],
        "grid": [{"old": item["source"].relative_to(data).as_posix(), "new": (data / GRID_REL / item["filename"]).relative_to(data).as_posix(), "sha256": item["sha256"]} for item in atlases],
        "transactions": [{k: v for k, v in item.items() if k != "document"} for item in transactions],
        "name_manifest_sha256": digest_bytes(canonical_json(name_manifest)),
    }
    plan_sha = digest_bytes(canonical_json(plan))
    return {"plan": plan, "plan_sha256": plan_sha, "protected_after_expectation": protected_after_expectation,
            "atlases": atlases, "sprites": sprites, "transactions": transactions, "name_manifest": name_manifest}


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.{os.urandom(5).hex()}.partial")
    try:
        with tmp.open("xb") as handle:
            handle.write(canonical_json(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def rename_by_sha(entries: list[dict[str, Any]], source_root: Path) -> int:
    renamed = 0
    for entry in entries:
        expected_sha = entry["sha256"]
        target = source_root / entry["filename"]
        source = entry["source"]
        if target.exists():
            if digest_bytes(target.read_bytes()) != expected_sha:
                raise ResetError(f"stable target name has different content: {target}")
            if source != target and source.exists():
                if digest_bytes(source.read_bytes()) != expected_sha:
                    raise ResetError(f"source changed during migration: {source}")
                source.unlink()
            continue
        if not source.is_file() or digest_bytes(source.read_bytes()) != expected_sha:
            raise ResetError(f"source changed during migration: {source}")
        temporary = source.with_name(f".lf-rp-migrate-{expected_sha}.partial")
        if temporary.exists():
            if digest_bytes(temporary.read_bytes()) != expected_sha:
                raise ResetError(f"migration temporary file has conflicting bytes: {temporary}")
            temporary.unlink()
        os.replace(source, temporary)
        os.replace(temporary, target)
        if digest_bytes(target.read_bytes()) != expected_sha:
            raise ResetError(f"post-rename hash mismatch: {target}")
        renamed += 1
    return renamed


def apply_plan(repository: Path, prepared: dict[str, Any]) -> dict[str, Any]:
    data = repository / "data"
    plan = prepared["plan"]
    # Verify the complete destructive set and protected trees before the first
    # write. This prevents a late mismatch from producing a partial reset.
    for rel_text, expected in plan["remove"].items():
        target = data / Path(rel_text)
        if not target.is_file() or digest_bytes(target.read_bytes()) != expected["sha256"]:
            raise ResetError(f"reset target changed after dry-run: {target}")
    for name, before in prepared["protected_after_expectation"].items():
        if file_inventory(data / name) != before:
            raise ResetError(f"protected owner data changed after dry-run: data/{name}")

    # Write fail-closed name metadata before renames; intake refuses PENDING state.
    name_manifest = dict(prepared["name_manifest"])
    name_manifest["migration_state"] = "PENDING"
    atomic_json(data / PIXELLAB_REL / NAME_MANIFEST, name_manifest)

    transaction_dir = data / PIXELLAB_REL / "Transactions"
    for transaction in prepared["transactions"]:
        destination = transaction_dir / Path(transaction["destination"]).name
        atomic_json(destination, transaction["document"])

    atlas_entries = [{"source": item["source"], "filename": item["filename"], "sha256": item["sha256"]} for item in prepared["atlases"]]
    sprite_entries = [{"source": item["source"], "filename": item["filename"], "sha256": item["sha256"]} for item in prepared["sprites"]]
    atlas_count = rename_by_sha(atlas_entries, data / GRID_REL)
    sprite_count = rename_by_sha(sprite_entries, data / FINAL_REL)

    # Remove exactly the dry-run set by root scope and stable hash checks.
    for rel in (RELEASE_POOL_REL, LEVEL_FACTORY_REL, LEGACY_ARCHIVE_REL):
        target = data / rel
        if target.exists():
            for path in walk_files(target):
                expected = plan["remove"].get(path.relative_to(data).as_posix())
                if expected is None or digest_bytes(path.read_bytes()) != expected["sha256"]:
                    raise ResetError(f"reset target changed after dry-run: {path}")
            shutil.rmtree(target)
    legacy_manifest = data / LEGACY_MANIFEST_REL
    if legacy_manifest.exists():
        expected = plan["remove"].get(LEGACY_MANIFEST_REL.as_posix())
        if expected is None or digest_bytes(legacy_manifest.read_bytes()) != expected["sha256"]:
            raise ResetError("legacy cleanup manifest changed after dry-run")
        legacy_manifest.unlink()
    keep_roots = [data / name for name in PROTECTED] + [data / FINAL_REL, data / GRID_REL, data / PIXELLAB_REL / "Transactions", data / PIXELLAB_REL / NAME_MANIFEST]
    for rel_text, expected in sorted(plan["remove"].items()):
        target = data / Path(rel_text)
        if not target.exists() or any(target == root or root in target.parents for root in keep_roots):
            continue
        if target.suffix.lower() != ".png":
            continue
        if target.is_file() and digest_bytes(target.read_bytes()) == expected["sha256"]:
            target.unlink()
        elif target.exists():
            raise ResetError(f"obsolete PNG changed after dry-run: {target}")

    # Recreate only canonical active directories after deleting legacy roots.
    for relative in (
        "Level Factory/Imported", "Level Factory/Batches/Imports", "Level Factory/Batches/Jobs",
        "Level Factory/Batches/Control", "Level Factory/Batches/Locks", "Level Factory/Activity",
        "Level Factory/Workspace/Candidates", "Level Factory/Workspace/Requests",
        "Level Factory/Workspace/Reproductions", "Level Factory/Workspace/Preset Runs",
        "Level Factory/Runtime", "Release Pool/Pending", "Release Pool/Ready",
        "Release Pool/Failed", "Release Pool/Rejected",
    ):
        (data / relative).mkdir(parents=True, exist_ok=True)

    # Final byte and protected-content checks, then make the metadata visible.
    for item in prepared["atlases"] + prepared["sprites"]:
        root = data / (GRID_REL if "atlas_filename" not in item else FINAL_REL)
        filename = item.get("filename")
        if "atlas_sha256" in item:
            root = data / FINAL_REL
        else:
            root = data / GRID_REL
        target = root / filename
        if not target.is_file() or digest_bytes(target.read_bytes()) != item["sha256"]:
            raise ResetError(f"PixelLab post-reset SHA verification failed: {target}")
    for name, before in prepared["protected_after_expectation"].items():
        after = file_inventory(data / name)
        if after != before:
            raise ResetError(f"protected owner data changed during reset: data/{name}")
    name_manifest["migration_state"] = "COMPLETE"
    name_manifest["renamed_at_utc"] = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
    atomic_json(data / PIXELLAB_REL / NAME_MANIFEST, name_manifest)
    # The reset plan contains prior paths/hashes only in memory and is not kept.
    return {"atlas_renamed": atlas_count, "sprites_renamed": sprite_count,
            "deleted_files": len(plan["remove"]), "deleted_bytes": sum(item["bytes"] for item in plan["remove"].values()),
            "protected_files_verified": sum(len(items) for items in prepared["protected_after_expectation"].values()),
            "atlases": len(prepared["atlases"]), "sprites": len(prepared["sprites"]),
            "pixel_linkage_verified": True, "plan_sha256": prepared["plan_sha256"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="execute the exact reset after matching a dry-run digest")
    parser.add_argument("--confirm-plan-sha256", help="digest printed by the matching --dry-run")
    parser.add_argument("--dry-run", action="store_true", help="read-only inventory and exact plan")
    args = parser.parse_args()
    try:
        prepared = build_plan(Path(__file__).resolve().parents[2])
        if args.apply:
            if args.confirm_plan_sha256 != prepared["plan_sha256"]:
                raise ResetError("apply requires the exact current --dry-run plan SHA-256")
            result = apply_plan(Path(prepared["plan"]["repository"]), prepared)
            print(json.dumps({"state": "APPLIED", **result}, ensure_ascii=False, sort_keys=True))
            return 0
        summary = {
            "state": "DRY_RUN", "plan_sha256": prepared["plan_sha256"],
            "protected_files": {name: len(files) for name, files in prepared["protected_after_expectation"].items()},
            "delete_count": len(prepared["plan"]["remove"]),
            "delete_bytes": sum(item["bytes"] for item in prepared["plan"]["remove"].values()),
            "release_pool_files": sum(path.startswith("Release Pool/") for path in prepared["plan"]["remove"]),
            "legacy_files": sum(path.startswith("legacy-level-cleanup-recovery-archive/") or path == LEGACY_MANIFEST_REL.as_posix() for path in prepared["plan"]["remove"]),
            "other_pngs": sum(path.lower().endswith(".png") and not path.startswith(("Release Pool/", "legacy-level-cleanup-recovery-archive/")) for path in prepared["plan"]["remove"]),
            "atlas_count": len(prepared["atlases"]), "final_sprite_count": len(prepared["sprites"]),
            "atlas_transaction_count": len(prepared["transactions"]), "exact_pixel_links": len(prepared["sprites"]),
            "filename_examples": {"atlas": [x["filename"] for x in prepared["atlases"][:3]], "final": [x["filename"] for x in prepared["sprites"][:3]]},
        }
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError, ResetError) as exc:
        print(json.dumps({"state": "ERROR", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
