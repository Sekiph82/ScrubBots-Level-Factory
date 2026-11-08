"""Bounded, non-recursive folder intake for owner-selected PNG sources."""

from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
import stat
from typing import Any, Callable

from .owner_art_storage import OwnerArtStorageError, _is_reparse_point, owner_art_paths
from .semantic.normalization.core import RAW_ARTIFACT_MAX_BYTES, SUPPORTED_MEDIA_TYPE, SemanticRawArtifact
from .owner_upload import owner_upload_root


_PROVIDER_KEYS = {
    "ALPIX": "alpix",
    "PIXELLAB": "pixellab_final",
    "OWNER_SUGGESTIONS": "owner_suggestions",
}


class OwnerFolderBatchError(ValueError):
    """Raised when an owner-selected source folder is outside the safe scope."""


class OwnerFolderProgressError(RuntimeError):
    """Raised when a progress event could not be durably recorded."""


def _pixellab_transaction_index(paths: dict[str, Path]) -> dict[str, dict[str, str]]:
    """Index atlas commit markers so interrupted 4x4 outputs cannot enter intake."""

    index: dict[str, dict[str, str]] = {}
    pending = paths["pending"]
    if not pending.exists():
        return index
    for manifest_path in sorted(pending.glob("pixellab-atlas-*.json"), key=lambda item: item.name):
        if _is_reparse_point(manifest_path) or not manifest_path.is_file():
            raise OwnerFolderBatchError("PixelLab atlas transaction manifest is unsafe")
        try:
            value = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise OwnerFolderBatchError("PixelLab atlas transaction manifest is unreadable") from exc
        atlas_sha = value.get("source_atlas_sha256") if isinstance(value, dict) else None
        state = value.get("state") if isinstance(value, dict) else None
        frames = value.get("frame_dimensions") if isinstance(value, dict) else None
        atlas_dimensions = value.get("atlas_dimensions") if isinstance(value, dict) else None
        slices = value.get("slices") if isinstance(value, dict) else None
        if (not isinstance(value, dict) or value.get("schema") != "scrubbots-pixellab-atlas-transaction/v1"
                or type(atlas_sha) is not str or len(atlas_sha) != 64
                or state not in {"IN_PROGRESS", "FINALIZED"}
                or not isinstance(frames, list) or len(frames) != 2 or any(type(part) is not int or not 51 <= part <= 59 for part in frames)
                or atlas_dimensions != [frames[0] * 4, frames[1] * 4]
                or value.get("atlas_filename") != f"atlas-{atlas_sha}.png"
                or not isinstance(slices, list) or len(slices) != 16
                or manifest_path.name != f"pixellab-atlas-{atlas_sha}.json"):
            raise OwnerFolderBatchError("PixelLab atlas transaction manifest contract is invalid")
        expected: dict[str, str] = {}
        for frame in slices:
            if not isinstance(frame, dict):
                raise OwnerFolderBatchError("PixelLab atlas transaction slice record is invalid")
            frame_index, frame_sha, filename = frame.get("index"), frame.get("sha256"), frame.get("filename")
            if (type(frame_index) is not int or not 1 <= frame_index <= 16
                    or type(frame_sha) is not str or len(frame_sha) != 64
                    or filename != f"atlas-{atlas_sha}-sprite-{frame_index:02d}-{frame_sha}.png"
                    or filename in expected):
                raise OwnerFolderBatchError("PixelLab atlas transaction slice identity is invalid")
            expected[filename] = frame_sha
        if set(expected) != {
                f"atlas-{atlas_sha}-sprite-{frame_index:02d}-{frame['sha256']}.png"
                for frame_index, frame in enumerate(sorted(slices, key=lambda row: int(row["index"])), 1)
        }:
            raise OwnerFolderBatchError("PixelLab atlas transaction must cover all sixteen row-major identities")
        group_valid = state == "FINALIZED"
        if group_valid:
            atlas_path = paths["pixellab_grid_files"] / str(value["atlas_filename"])
            group_valid = not _is_reparse_point(atlas_path) and atlas_path.is_file()
            if group_valid:
                group_valid = hashlib.sha256(atlas_path.read_bytes()).hexdigest() == atlas_sha
            for filename, digest in expected.items():
                slice_path = paths["pixellab_final"] / filename
                if _is_reparse_point(slice_path) or not slice_path.is_file():
                    group_valid = False
                    break
                try:
                    artifact = SemanticRawArtifact.from_local_file(slice_path, media_type=SUPPORTED_MEDIA_TYPE)
                    actual_sha = hashlib.sha256(bytes(artifact.raw_bytes)).hexdigest()
                except (OSError, TypeError, ValueError):
                    group_valid = False
                    break
                if (actual_sha != digest or (artifact.returned_width, artifact.returned_height) != tuple(frames)):
                    group_valid = False
                    break
        for filename, digest in expected.items():
            if filename in index:
                raise OwnerFolderBatchError("PixelLab transaction manifests reuse a Final filename")
            index[filename] = {"state": str(state), "sha256": digest, "group_valid": "true" if group_valid else "false"}
    return index


def approved_owner_source_folders(repository_root: str | Path | None = None) -> dict[str, Path]:
    paths = owner_art_paths(repository_root)
    return {provider: paths[key] for provider, key in _PROVIDER_KEYS.items()}


def scan_owner_source_folder(
    folder_path: str | Path,
    *,
    repository_root: str | Path | None = None,
    explicit_alternative: bool = False,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """List direct-child PNG candidates; the canonical importer validates bytes.

    Only the three canonical owner folders are accepted. The legacy explicit
    alternative flag is retained for wire compatibility but grants no access to
    other artwork locations. Traversal is never recursive and PixelLab raw atlas
    storage is always excluded.
    """
    paths = owner_art_paths(repository_root)
    root = paths["input"].parents[1]
    raw_text = str(folder_path)
    raw_folder = Path(raw_text).expanduser()
    path_parts = re.split(r"[\\/]+", raw_text)
    if not raw_folder.is_absolute() or any(part in {".", ".."} for part in path_parts):
        raise OwnerFolderBatchError("selected source path must be an absolute canonical folder path")
    resolved_folder = raw_folder.resolve(strict=True)
    if _is_reparse_point(root):
        raise OwnerFolderBatchError("canonical repository root is a reparse point")
    cursor = raw_folder
    while cursor != cursor.parent:
        if _is_reparse_point(cursor):
            raise OwnerFolderBatchError("selected source path contains a symlink or reparse point")
        cursor = cursor.parent
    if not resolved_folder.is_dir():
        raise OwnerFolderBatchError("selected source is not a directory")

    grid_root = paths["pixellab_grid_files"].resolve(strict=False)
    if resolved_folder == grid_root or grid_root in resolved_folder.parents:
        raise OwnerFolderBatchError("PixelLab Grid Files stores raw atlases and is never a single-level intake source")

    provider = next((name for name, approved in approved_owner_source_folders(root).items()
                     if resolved_folder == approved.resolve(strict=False)), "")
    if not provider:
        raise OwnerFolderBatchError("source folder is not one of the canonical owner artwork folders")
    if progress_callback is not None:
        try:
            progress_callback({"stage": "FOLDER", "state": "RUNNING", "message": "Canonical folder selected; checking atlas provenance and listing direct PNG files."})
        except Exception as exc:
            raise OwnerFolderProgressError("folder preview progress could not be recorded") from exc
    transaction_index: dict[str, dict[str, str]] = {}
    if provider == "PIXELLAB":
        if progress_callback is not None:
            try:
                progress_callback({"stage": "ATLAS PROVENANCE", "state": "RUNNING", "message": "Checking PixelLab atlas transaction manifests before PNG discovery."})
            except Exception as exc:
                raise OwnerFolderProgressError("atlas provenance progress could not be recorded") from exc
        transaction_index = _pixellab_transaction_index(paths)
        if progress_callback is not None:
            try:
                progress_callback({"stage": "ATLAS PROVENANCE", "state": "PASS", "message": f"Atlas provenance check complete; {len(transaction_index)} transaction records indexed."})
            except Exception as exc:
                raise OwnerFolderProgressError("atlas provenance result could not be recorded") from exc

    png_files: list[Path] = []
    for entry in resolved_folder.iterdir():
        if entry.suffix.lower() != ".png":
            continue
        if _is_reparse_point(entry):
            raise OwnerFolderBatchError(f"PNG candidate is a symlink or reparse point: {entry.name}")
        if not entry.is_file():
            continue
        mode = entry.stat().st_mode
        if not stat.S_ISREG(mode):
            continue
        png_files.append(entry)
    png_files.sort(key=lambda item: (item.name.casefold(), item.name))
    if progress_callback is not None:
        try:
            progress_callback({"stage": "DISCOVERY", "state": "RUNNING", "completed": 0,
                               "total": len(png_files), "message": f"Found {len(png_files)} direct PNG files; starting per-file validation."})
        except Exception as exc:
            raise OwnerFolderProgressError("folder discovery progress could not be recorded") from exc
    entries: list[dict[str, Any]] = []
    valid_paths: list[str] = []
    rejected: list[dict[str, Any]] = []
    seen_digests: set[str] = set()
    seen_names: dict[str, str] = {}
    existing_sources = owner_upload_root(repository_root)

    def record_entry(result: dict[str, Any], item_index: int) -> None:
        entries.append(result)
        if progress_callback is None:
            return
        disposition = str(result.get("disposition", "REJECTED"))
        reason = str(result.get("reason", ""))
        dimensions = ""
        if type(result.get("width")) is int and type(result.get("height")) is int:
            dimensions = f" {result['width']}x{result['height']}"
        detail = f"{item_index + 1}/{len(png_files)} {item.name}{dimensions} — {disposition}"
        if reason:
            detail += f" — {reason}"
        try:
            progress_callback({"stage": "FILE CHECK", "state": disposition,
                               "completed": item_index + 1, "total": len(png_files),
                               "filename": item.name, "disposition": disposition,
                               "message": detail[:240]})
        except Exception as exc:
            raise OwnerFolderProgressError("per-file folder preview progress could not be recorded") from exc

    for index, item in enumerate(png_files):
        transaction = transaction_index.get(item.name)
        if transaction is not None and (transaction["state"] != "FINALIZED" or transaction["group_valid"] != "true"):
            result = {
                "index": index, "path": str(item), "display_path": item.name,
                "disposition": "REJECTED", "reason": "PIXELLAB_ATLAS_TRANSACTION_INCOMPLETE_OR_INVALID",
            }
            record_entry(result, index)
            rejected.append({
                "index": index, "display_path": item.name, "original_source_path": str(item),
                "error": result["reason"],
            })
            continue
        try:
            if item.stat().st_size > RAW_ARTIFACT_MAX_BYTES:
                raise OwnerFolderBatchError("PNG exceeds the bounded source size")
            artifact = SemanticRawArtifact.from_local_file(item, media_type=SUPPORTED_MEDIA_TYPE)
            width, height = artifact.returned_width, artifact.returned_height
            digest = hashlib.sha256(bytes(artifact.raw_bytes)).hexdigest()
            if provider == "PIXELLAB" and not (51 <= width <= 59 and 51 <= height <= 59):
                result = {
                    "index": index, "path": str(item), "display_path": item.name,
                    "source_sha256": digest, "width": width, "height": height,
                    "disposition": "REJECTED", "reason": "PIXELLAB_FINAL_DIMENSIONS_MUST_BE_51_TO_59_PIXELS",
                }
                record_entry(result, index)
                rejected.append({
                    "index": index, "display_path": item.name, "original_source_path": str(item),
                    "source_sha256": digest, "original_width": width, "original_height": height,
                    "error": result["reason"],
                })
                continue
            if transaction is not None and digest != transaction["sha256"]:
                raise OwnerFolderBatchError("PixelLab Final PNG no longer matches its finalized atlas manifest")
            result = {
                "index": index, "path": str(item), "display_path": item.name, "source_sha256": digest,
                "width": width, "height": height, "disposition": "ELIGIBLE",
            }
            filename_key = item.name.casefold()
            previous_digest = seen_names.get(filename_key)
            if previous_digest is not None and previous_digest != digest:
                result["filename_collision"] = True
                result["collision_with_sha256"] = previous_digest
                for prior_entry in entries:
                    if str(prior_entry.get("display_path", "")).casefold() == filename_key:
                        prior_entry["filename_collision"] = True
                        prior_entry["collision_with_sha256"] = digest
            else:
                seen_names[filename_key] = digest
            if not 20 <= width <= 59 or not 20 <= height <= 59:
                result["disposition"] = "REJECTED"
                result["reason"] = "GAME_ARTWORK_DIMENSIONS_MUST_BE_20_TO_59_PIXELS"
                rejected.append({
                    "index": index, "display_path": item.name, "original_source_path": str(item),
                    "source_sha256": digest, "original_width": width, "original_height": height,
                    "error": result["reason"],
                })
            else:
                source_id = f"owner-upload-{digest}"
                if digest in seen_digests:
                    result["disposition"] = "SKIPPED_DUPLICATE"
                    result["reason"] = "DUPLICATE_IDENTICAL_SHA256_IN_SELECTED_FOLDER"
                elif (existing_sources / source_id).exists():
                    from . import studio_extensions
                    try:
                        studio_extensions.verify_owner_source(source_id)
                        result["disposition"] = "ALREADY_IMPORTED"
                        result["reason"] = "IDENTICAL_SHA256_ALREADY_IMPORTED"
                    except (studio_extensions.StudioExtensionError, OSError, ValueError) as exc:
                        result["disposition"] = "FAILED"
                        result["reason"] = f"EXISTING_SOURCE_IDENTITY_CONFLICT: {str(exc)[:300]}"
                        rejected.append({
                            "index": index, "display_path": item.name, "original_source_path": str(item),
                            "source_sha256": digest, "original_width": width, "original_height": height,
                            "error": result["reason"], "disposition": "FAILED",
                        })
                seen_digests.add(digest)
                if result["disposition"] != "FAILED":
                    valid_paths.append(str(item))
            record_entry(result, index)
        except (OSError, TypeError, ValueError, OwnerArtStorageError) as exc:
            reason = str(exc)[:400] or "PNG could not be validated"
            result = {"index": index, "path": str(item), "display_path": item.name,
                      "disposition": "REJECTED", "reason": reason}
            record_entry(result, index)
            rejected.append({"index": index, "display_path": item.name,
                             "original_source_path": str(item), "error": reason})
    return {
        "provider": provider,
        "selected_folder": str(resolved_folder),
        "png_count": len(png_files),
        "paths": valid_paths,
        "entries": entries,
        "pre_rejected": rejected,
    }


def import_owner_source_folder(
    folder_path: str | Path,
    *,
    repository_root: str | Path | None = None,
    explicit_alternative: bool = False,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Import a bounded owner folder through canonical OWNER_UPLOAD hashing."""
    scanned = scan_owner_source_folder(
        folder_path,
        repository_root=repository_root,
        explicit_alternative=explicit_alternative,
        progress_callback=progress_callback,
    )
    from . import studio_extensions

    payload = studio_extensions.batch_import(
        scanned["paths"],
        source_provider=scanned["provider"],
        source_folder=scanned["selected_folder"],
        pre_rejected=scanned["pre_rejected"],
        # `paths` also includes hash-identical sources that already have an
        # immutable OWNER_UPLOAD record. Keep indices aligned with every path
        # that is passed to batch_import, or an all-ALREADY_IMPORTED folder
        # fails before the UI can load/select its existing sources.
        path_indices=[
            int(item["index"])
            for item in scanned["entries"]
            if item.get("disposition") in {"ELIGIBLE", "ALREADY_IMPORTED"}
        ],
        progress_callback=progress_callback,
    )
    return {**payload, "source_provider": scanned["provider"],
            "source_folder": scanned["selected_folder"], "png_count": scanned["png_count"]}


__all__ = [
    "OwnerFolderBatchError", "approved_owner_source_folders",
    "import_owner_source_folder", "scan_owner_source_folder",
]
